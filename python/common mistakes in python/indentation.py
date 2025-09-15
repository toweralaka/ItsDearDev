def remove_from_stock(fifo_data, branch, quantity, ref_code):
    remainder = quantity
    returns_list = fifo_data[0]
    stock_list = fifo_data[1]
    for returns in returns_list:
        if remainder > 0:
            if returns.balance > remainder:
                returns.balance -= remainder
                remainder = 0
            elif returns.balance < remainder:
                remainder -= returns.balance
                returns.balance = 0
    for pdt in stock_list:
        if remainder > 0:
            if pdt.balance >= remainder:
                pdt.balance -= remainder
                remainder = 0
            else:
                remainder = remainder - pdt.balance
                pdt.balance = 0
            pdt.comment = update_stock_comment(pdt.comment, ref_code)

# Indentation error 1
def square_highest_based_on_cap(a, b, cap):
    if (a < cap) and (b < cap):
        if a > b:
            return a**2
        else:
            return b**2
    else:
        return cap


# indentation error 2
def greet():
    print("Hello, world!")


# tab, spaces mix
def square_if_even(number):
    if (number % 2) == 0:
        return number**2
    return number

# # tab, spaces mix


def square_if_even(number):
    if (number % 2) == 0:
	    return number**2
    return number


# # Indentation error 1
# def square_highest_based_on_cap(a, b, cap):


# if (a < cap) and (b < cap):
# if a > b:
# return a**2
# else:
# return b**2
# else:
# return cap


# # indentation error 2
# def greet():
# print("Hello, world!")


# # tab, spaces mix
# def square_if_even(number):
# 	if (number % 2) == 0:
# 		return number**2
# 	return number

# # tab, spaces mix


# def square_if_even(number):
#     if (number % 2) == 0:
# 		return number**2
#     return number
