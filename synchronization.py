def sync_delay (beetles_delay1, beetles_delay2, beetles_delay3, offset):
    delay = 0
    if(beetles_delay1 is None ):
        return -1
    max = max(beetles_delay1, beetles_delay2, beetles_delay3)
    min = min(beetles_delay1, beetles_delay2, beetles_delay3)
    delay = max - min - offset
    return delay