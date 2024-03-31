def merge_sorted_arrays(arr1, arr2):
    final_arr = []
    n = len(arr1)
    m = len(arr2)
    i = 0
    j = 0
    while i<n or j<m :
        if (i<n and j>=m) or ((i<n and j<m) and (arr1[i] <= arr2[j])) :
            final_arr.append(arr1[i])
            i+=1
        elif (i>=n and j<m) or ((i<n and j<m) and (arr1[i] > arr2[j])) :
            final_arr.append(arr2[j])
            j+=1
    
    return final_arr


arr1 = [1,4,5]
arr2 = [2,6]

print(merge_sorted_arrays(arr1,arr2))