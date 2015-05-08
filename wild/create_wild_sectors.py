"""
Serve a convertire una immagine wild di altitudini, creata con il worldgen, in
una immagine wild di settori da cui partire per poi inserirvi il resto: strade,
fiumi, città, etc etc...
"""

import Image

altitude_colors = (
     ((  0,   0,  68), -15),  # Oceani, mari o laghi
     ((  0,  17, 102), -14),
     ((  0,  51, 136), -13),
     ((  0,  85, 170), -12),
     ((  0, 119, 187), -11),
     ((  0, 153, 221), -10),
     ((  0, 204, 255),  -9),
     (( 34, 221, 255),  -8),
     (( 68, 238, 255),  -7),
     ((102, 255, 255),  -6),
     ((119, 255, 255),  -5),
     ((136, 255, 255),  -4),
     ((153, 255, 255),  -3),
     ((170, 255, 255),  -2),
     ((187, 255, 255),  -1),
     ((  0,  68,   0),   0),  # Settori di pianura, poco sopra il livello del mare
     (( 34, 102,   0),   1),
     (( 34, 136,   0),   2),
     ((119, 170,   0),   3),
     ((187, 221,   0),   4),  # Settori di collina
     ((255, 187,  34),   5),
     ((238, 170,  34),   6),
     ((221, 136,  34),   7),
     ((204, 136,  34),   8),  # Settori di montagna
     ((187, 102,  34),   9),
     ((170,  85,  34),  10),
     ((153,  85,  34),  11),
     ((136,  68,  34),  12),  # Settori di picchi
     ((119,  51,  34),  13),
     (( 85,  51,  17),  14),
     (( 68,  34,   0),  15))

altitude_to_sector = {
    -15 : (  0,  51, 136),
    -14 : (  0,  51, 136),
    -13 : (  0,  51, 136),
    -12 : (  0,  51, 136),
    -11 : (  0,  51, 136),
    -10 : (  0,  51, 136),
     -9 : (  0,  51, 136),
     -8 : (  0,  51, 136),
     -7 : (  0,  51, 136),
     -6 : (  0,  51, 136),
     -5 : (  0,  51, 136),
     -4 : (  0,  51, 136),
     -3 : (  0,  51, 136),
     -2 : (  0,  51, 136),
     -1 : (  0,  51, 136),
      0 : ( 34, 136,   0),
      1 : ( 34, 136,   0),
      2 : ( 34, 136,   0),
      3 : ( 34, 136,   0),
      4 : (238, 170,  34),
      5 : (238, 170,  34),
      6 : (238, 170,  34),
      7 : (238, 170,  34),
      8 : (187, 102,  34),
      9 : (187, 102,  34),
     10 : (187, 102,  34),
     11 : (187, 102,  34),
     12 : (119,  51,  34),
     13 : (119,  51,  34),
     14 : (119,  51,  34),
     15 : (119,  51,  34)}


if __name__ == "__main__":
    im = Image.open("altitudes.png")
    width = im.size[0]
    height = im.size[1]
    im2 = Image.new("RGB", (width, height))
    altitudes = [[0 for y in range(height)] for x in range(width)]
    sectors = [[0 for y in range(height)] for x in range(width)]
    for x in range(width):
        for y in range(height):
            r, g, b = im.getpixel((x, y))
            for ac in altitude_colors:
                if (r, g, b) == ac[0]:
                    altitudes[x][y] = ac[1]
                    im2.putpixel((x, y), altitude_to_sector[ac[1]])
    im2.save("sectors.png", "PNG")
