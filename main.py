# Code allowing reading of and writing to PNG files

# Read width and height of the image
def from_bytes(b: bytes):
    return int.from_bytes(b, "big")

class ChunkProperties:
    def __init__(self, chunkType: bytes):
        # Set each property by determining whether each byte represents an upper or lower case letter
        propertyValues = [bool((byte >> 5) & 1) for byte in chunkType]
        self.ancillary = propertyValues[0] # If uppercase, chunk is critical to the image
        self.public = propertyValues[1] # If uppercase, chunk is public (part of the PNG specification)
        # Third property is reserved for future use
        self.safeToCopy = propertyValues[3] # If uppercase, chunk is not safe to copy if the image is changed

class Chunk:
    def __init__(self, length: int, chunkType: bytes, data: bytes, crc: bytes):
        self.length = length
        self.chunkType = chunkType.decode("utf-8")
        self.data = data
        self.crc = crc
        self.pos = 0
        self.properties = ChunkProperties(chunkType)

    def read(self, numBytes: int):
        self.pos += numBytes
        return self.data[self.pos - numBytes:self.pos]

class PngReader:
    def __init__(self, f: str):
        # Open the specified file in binary mode
        self.file = open(f, "rb")

        # Read the first 8 bytes of the file and compare against the standard PNG header
        header = [from_bytes(self.file.read(1)) for i in range(8)]
        if not header == [137, 80, 78, 71, 13, 10, 26, 10]:
            # If the file is not a PNG, throw an exception
            raise Exception("Input is not a valid PNG file")
        
        # Read the first chunk of the file (should be the IHDR chunk - Image Header)
        IHDR = self.readChunk()
        if IHDR.chunkType != "IHDR":
            # IHDR must be the first chunk of the file, throw and error if it isn't
            raise Exception("Input is not a valid PNG file")
        
        """
        The IHDR chunk contains the following data:
        Width: 4 bytes
        Height: 4 bytes
        Bit depth (Number of bits per color component): 1 byte
        Color type: 1 byte
        Compression method: 1 byte
        Filter method: 1 byte
        Interlace method: 1 byte
        TODO: Idk what the last 3 are, implement later
        """
        self.width = from_bytes(IHDR.read(4))
        self.height = from_bytes(IHDR.read(4))

        print(f"Width: {self.width}, Height: {self.height}")

        # Close the file after reading
        self.close()

    def readChunk(self):
        """
        Each chunk always consists of four parts:
        Length: 4 bytes
        Chunk type (number of bytes of data): 4 bytes
        Chunk data: <length> bytes
        CRC (TODO: Implement check): 4 bytes
        """
        length = from_bytes(self.file.read(4))
        chunkType = self.file.read(4)
        data = self.file.read(length)
        crc = self.file.read(4)

        return Chunk(length, chunkType, data, crc)

    def close(self):
        self.file.close()

if __name__ == "__main__":
    test = PngReader("test.png")