from io import BytesIO
import json

FILE_PATH = "MediaCatalog.bytes" # Edit here


CHAR_LENGTH = 1
SHORT_LENGTH = 2
INT_LENGTH = 4
LONG_LENGTH = 8

class MediaCatalogBytes:
    def __init__(self, byte_data=None) -> None:
        self._converted_data = None
        if byte_data is None:
            with open(FILE_PATH, 'rb') as f:
                byte_data = f.read()
        self._data = BytesIO(byte_data)

    def _read_int(self, length):
        b = self._data.read(length)
        return int.from_bytes(b, 'little')

    def _read_str(self, length):
        return self._data.read(length).decode()
    
    def _read_string_item(self):
        unknown     = self._read_int(INT_LENGTH) # Unknown
        string_len  = self._read_int(INT_LENGTH) # Length of String Item
        string      = self._read_str(string_len) # String Item
        assert unknown + string_len == 0xFFFFFFFF, f'Incorrect string item length? {string}'
        return string
    
    def convert_to_dict(self):
        """
        header
            unknown_info: char
            header_length: uint

        content
            # Sum of each Unknown and Length should be equal to 0xFFFFFFFF
            # ...why?

            unknown_1: uint
            content_key_len: uint
            content_key: str

            unknown_2: char
            
            unknown_3: uint
            path_len: uint
            path: str

            unknown_4: uint
            FileName_len: uint
            FileName: str

            Bytes: long
            Crc: long
            IsPrologue: short
            MediaType: uint
        """
        if self._converted_data:
            return self._converted_data
        
        contents = {}

        # Header
        unknown_info = self._read_int(CHAR_LENGTH) #Unknown
        contents_len = self._read_int(INT_LENGTH) # Num of All contents in this file

        # Main Contents
        while len(contents) < contents_len:
            # Content Key
            content_key     = self._read_string_item()

            # Unknown_2
            unknown_2       = self._read_int(CHAR_LENGTH) # Unknown: usually 0x07
            assert unknown_2 == 0x07, f'What is this? content_key: {content_key}'

            # path
            path            = self._read_string_item()

            # FileName
            file_name       = self._read_string_item()

            # Other Info
            size_bytes      = self._read_int(LONG_LENGTH) # Content Size in Bytes
            crc             = self._read_int(LONG_LENGTH) # CRC
            is_prologue     = self._read_int(SHORT_LENGTH) # Is Prologue
            media_type      = self._read_int(INT_LENGTH)

            content = dict(
                MediaType   = media_type,
                path        = path,
                FileName    = file_name,
                Bytes       = size_bytes,
                Crc         = crc,
            )

            if is_prologue:
                # This field is usually missing unless the value is True
                content['IsPrologue'] = False

            contents[content_key] = content

        table = dict(
            Table = contents
        )

        self._converted_data = table
        return table


if __name__ == '__main__':
    print('Start converting MediaCatalog.bytes')

    catalog = MediaCatalogBytes()
    table = catalog.convert_to_dict()

    with open('MediaCatalog.json', 'w') as f:
        json.dump(table, f)
    
    print('Done!')
