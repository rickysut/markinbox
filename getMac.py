# Python 3 code to print MAC
# in formatted way.

import uuid
mac1=uuid.getnode()
mac2=hex(uuid.getnode())

print(mac1)  ## langsung
print(mac2)  #$ format hexa
