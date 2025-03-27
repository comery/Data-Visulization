# -*- coding: utf-8 -*-

bed_list = [[4,5], [8,9], [2,6], [1,2]]
sort_bed_list = list(sorted(bed_list))
result_list = []
mapped_length = 0

low_est = sort_bed_list[0][0]
high_est = sort_bed_list[0][1]

for i in range(1, len(sort_bed_list)):
    low, high = sort_bed_list[i]
    if high_est >= low:
        if high_est < high:
            high_est = high
    else:
        result_list.append([low_est, high_est])
        low_est, high_est = sort_bed_list[i]
result_list.append([low_est, high_est])
print(result_list)
for i in result_list:
    a,b = i
    mapped_length += (b - a + 1)

print(mapped_length)
