from my_m3u8 import *


m3u8_url = 'http://devimages.apple.com/iphone/samples/bipbop/bipbopall.m3u8'


if __name__ == '__main__':
    m3u8 = M3U8(Client(), m3u8_url)
    m3u8.print()     # it contains urls of .m3u8, not encrypted
    m3u8 = m3u8.get_m3u8(2)
    m3u8.print()     # it contains urls of .ts, not encrypted
    m3u8.get_ts('/Users/jtian/Desktop/test.ts')
