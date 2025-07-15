import struct
from enum import IntEnum
from typing import List, Optional, Tuple

class VariantType(IntEnum):
    UNKNOWN = 0
    FLOAT = 1
    STRING = 2
    VEC2 = 3
    VEC3 = 4
    UNSIGNED = 5
    SIGNED = 9

class Variant:
    def __init__(self, value, variant_type: VariantType):
        self.value = value
        self.variant_type = variant_type
    
    def as_string(self) -> str:
        if self.variant_type == VariantType.FLOAT:
            return str(self.value)
        elif self.variant_type == VariantType.STRING:
            return self.value
        elif self.variant_type == VariantType.VEC2:
            return f"{self.value[0]}, {self.value[1]}"
        elif self.variant_type == VariantType.VEC3:
            return f"{self.value[0]}, {self.value[1]}, {self.value[2]}"
        elif self.variant_type == VariantType.UNSIGNED:
            return str(self.value)
        elif self.variant_type == VariantType.SIGNED:
            return str(self.value)
        else:
            return "Unknown"
    
    def as_int32(self) -> int:
        if self.variant_type == VariantType.SIGNED:
            return self.value
        return 0
    
    def as_vec2(self) -> Tuple[float, float]:
        if self.variant_type == VariantType.VEC2:
            return self.value
        return (0.0, 0.0)
    
    def as_uint32(self) -> int:
        if self.variant_type == VariantType.UNSIGNED:
            return self.value
        return 0
    
    def as_float(self) -> float:
        if self.variant_type == VariantType.FLOAT:
            return self.value
        return 0.0
    
    def as_vec3(self) -> Tuple[float, float, float]:
        if self.variant_type == VariantType.VEC3:
            return self.value
        return (0.0, 0.0, 0.0)
    
    def __repr__(self):
        return f"Variant({self.variant_type.name}: {self.value})"

class VariantList:
    def __init__(self):
        self.variants: List[Variant] = []
    
    @classmethod
    def deserialize(cls, data: bytes) -> 'VariantList':
        if len(data) == 0:
            raise ValueError("Empty data")
        
        variant_list = cls()
        offset = 0
        
        size = data[offset]
        offset += 1
        
        for _ in range(size):
            if offset >= len(data):
                raise ValueError("Unexpected end of data")
            
            _index = data[offset]
            offset += 1
            
            if offset >= len(data):
                raise ValueError("Unexpected end of data")
            var_type = VariantType(data[offset])
            offset += 1
            
            if var_type == VariantType.FLOAT:
                if offset + 4 > len(data):
                    raise ValueError("Not enough data for float")
                value = struct.unpack('<f', data[offset:offset+4])[0]
                offset += 4
                variant = Variant(value, var_type)
                
            elif var_type == VariantType.STRING:
                if offset + 4 > len(data):
                    raise ValueError("Not enough data for string length")
                length = struct.unpack('<I', data[offset:offset+4])[0]
                offset += 4
                
                if offset + length > len(data):
                    raise ValueError("Not enough data for string content")
                value = data[offset:offset+length].decode('utf-8')
                offset += length
                variant = Variant(value, var_type)
                
            elif var_type == VariantType.VEC2:
                if offset + 8 > len(data):
                    raise ValueError("Not enough data for vec2")
                x, y = struct.unpack('<ff', data[offset:offset+8])
                offset += 8
                variant = Variant((x, y), var_type)
                
            elif var_type == VariantType.VEC3:
                if offset + 12 > len(data):
                    raise ValueError("Not enough data for vec3")
                x, y, z = struct.unpack('<fff', data[offset:offset+12])
                offset += 12
                variant = Variant((x, y, z), var_type)
                
            elif var_type == VariantType.UNSIGNED:
                if offset + 4 > len(data):
                    raise ValueError("Not enough data for unsigned")
                value = struct.unpack('<I', data[offset:offset+4])[0]
                offset += 4
                variant = Variant(value, var_type)
                
            elif var_type == VariantType.SIGNED:
                if offset + 4 > len(data):
                    raise ValueError("Not enough data for signed")
                value = struct.unpack('<i', data[offset:offset+4])[0]
                offset += 4
                variant = Variant(value, var_type)
                
            else:  # VariantType.UNKNOWN
                variant = Variant(None, var_type)
            
            variant_list.variants.append(variant)
        
        return variant_list
    
    def get(self, index: int) -> Optional[Variant]:
        if 0 <= index < len(self.variants):
            return self.variants[index]
        return None
    
    def __len__(self):
        return len(self.variants)
    
    def __getitem__(self, index):
        return self.variants[index]
    
    def __iter__(self):
        return iter(self.variants)
    
    def __repr__(self):
        return f"VariantList({self.variants})"
