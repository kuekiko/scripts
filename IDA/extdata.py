import idc

start_addr = 0x1400134B0
end_addr = 0x140053708

data = []
for i in range(end_addr-start_addr):{
    data.append(idc.get_wide_byte(start_addr+i))
}
# print(data)
data1 = []
key = "47fe0f2b13ca4739306eb3e6442e2f0f6adf2ddde783c56da721fb3f56647d1baff7ef6e0adae9deeecd864ce8df3ca3"
j = 0
for i in data:
    data1.append(i^ord(key[j]))
    j += 1
    j = j%96

# print(data1)

for i in range(end_addr-start_addr):{
    idc.patch_byte(start_addr+i,data1[i])
}

# idaapi.MakeCode(start_addr)
# idc.AutoMark(start_addr,idc.AU_CODE)
idc.plan_and_wait(start_addr,end_addr)