def remove_remark(string):
    if string is None:
        return ''
    find_list = ['(', '（', '备注']
    index = len(string)
    for find_str in find_list:
        i = string.find(find_str)
        if i != -1 and i < index:
            index = i
    return string[:index].strip()
