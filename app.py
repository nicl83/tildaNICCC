import app
import math
import time

from events.input import Buttons, BUTTON_TYPES

class TildaNICCC(app.App):
    def __init__(self):
        self.button_states = Buttons(self)
        self.niccc_handle = open('/apps/tildaNICCC/STNICCC-data.bin', 'rb')
        self.prev_pos = 0
        self.niccc_palette = [(0, 0, 0) for _ in range(0,16)]

        self.benchmark_mode = True

        self.demo_done = False
        self.congrats = False
        self.demo_start_time = time.time()

    def update(self, delta):
        if self.button_states.get(BUTTON_TYPES["CANCEL"]):
            self.button_states.clear()
            self.niccc_handle.seek(0)
            self.demo_done = False
            self.minimise()
        elif self.button_states.get(BUTTON_TYPES["CONFIRM"]):
            self.button_states.clear()
            self.benchmark_mode = not self.benchmark_mode

    def draw(self, ctx):
        if not self.benchmark_mode:
            time.sleep_ms(33)
        
        if not self.demo_done:
            self.niccc_demo(ctx)
        else:
            ctx.rgb(*self.niccc_palette[0]).rectangle(-120,-120,240,240).fill() # clear screen
            if self.congrats == False:
                print(f"FINISH! demo took {time.time() - self.demo_start_time}s")
                self.congrats = True

    def niccc_demo(self, ctx, print_debug=False):
        # -1 - STOP, 0xFD byte encountered at end of frame
        # 0 - header byte
        # 1 - palette (sometimes)
        # 2 - vertexes
        # 3 - polygons
        machine_state = 0

        while machine_state != -1:
            if machine_state == 0:

                frame_header = int.from_bytes(self.niccc_handle.read(1), 'big')

                if frame_header & 1:
                    ctx.rgb(*self.niccc_palette[0]).rectangle(-120,-120,240,240).fill() # clear screen

                if frame_header & 2:
                    machine_state = 1 # palette needs to be unpacked
                else:
                    machine_state = 2 # skip to vertexes

                if frame_header & 4:
                    indexed_mode = True
                else:
                    indexed_mode = False
                    if not frame_header & 2:
                        # palette code will handle index flag correctly
                        # but if that doesn't trigger, weird shit happens
                        machine_state = 3
            elif machine_state == 1:
                palette_bitfield = int.from_bytes(self.niccc_handle.read(2), 'big')
                for expo in range(16,-1, -1):
                    if (palette_bitfield & (2**expo)):
                        color = parse_st_colour(int.from_bytes(self.niccc_handle.read(2), 'big'))
                        self.niccc_palette[15-expo] = color

                if indexed_mode:
                    machine_state = 2
                else:
                    machine_state = 3
                
            elif machine_state == 2:
                vertexes = []
                expected_vertex_count = int.from_bytes(self.niccc_handle.read(1), 'big')

                for _ in range(0,expected_vertex_count):
                    # xy = self.niccc_handle.read(2)
                    # x = int.from_bytes(self.niccc_handle.read(1), 'big')
                    # y = int.from_bytes(self.niccc_handle.read(1), 'big')
                    vertexes.append(
                        (
                            int.from_bytes(self.niccc_handle.read(1), 'big'), # x 
                            int.from_bytes(self.niccc_handle.read(1), 'big')  # y
                        )
                    )

                machine_state = 3

            elif machine_state == 3:
                poly_header = int.from_bytes(self.niccc_handle.read(1), 'big')
                if poly_header == 0xFF:
                    return
                elif poly_header == 0xFE:
                    self.niccc_handle.seek((65536 * (math.ceil(self.niccc_handle.tell()/65536))))
                    return
                elif poly_header == 0xFD:
                    machine_state = -1
                else:
                    pal_index = poly_header >> 4
                    vert_count = poly_header & 0xF
                    
                    ctx.rgb(*self.niccc_palette[pal_index])
                    if indexed_mode:
                        for n in range(0, vert_count):
                            vert = vertexes[int.from_bytes(self.niccc_handle.read(1), 'big')]
                            if n == 0:
                                ctx.move_to(-128+vert[0], -100+vert[1])
                            else:
                                ctx.line_to(-128+vert[0], -100+vert[1])
                    else:
                        for n in range(0, vert_count):
                            x = int.from_bytes(self.niccc_handle.read(1), 'big')
                            y = int.from_bytes(self.niccc_handle.read(1), 'big')
                            if n == 0:
                                ctx.move_to(-128+x, -100+y)
                            else:
                                ctx.line_to(-128+x, -100+y)
                    ctx.close_path()
                    ctx.fill()

        self.demo_done = True
        self.niccc_handle.close()
        return

def parse_st_colour(x):
    "Parse ST colour to 0-255 tuple"
    r = (x & 0x700) >> 8
    g = (x & 0x70) >> 4
    b = x & 0x7
    return ((ste_color(r)*16)/255, (ste_color(g)*16)/255, (ste_color(b)*16)/255)

def ste_color(x):
    "Due to Jack Tramiel, we have to do weird math to colour nibbles"
    # bit_three = (x & 0x8) >> 3
    # low_bits = (x & 0x7) << 1
    return ((x & 0x7) << 1) + ((x & 0x8) >> 3)

__app_export__ = TildaNICCC