from math import ceil, sqrt

def find_prime(start: int, end: int) -> list:
    result = []
    for i in range(start, end + 1):
        isPrime: bool = True
        if (i >= 2):
            for k in range(2, ceil(sqrt(i) + 0.5)):
                if i % k == 0:
                    isPrime = False
                    break
        else:
            isPrime: bool = False
        if (isPrime): result.append(i)
    return result


if __name__ == '__main__':
    print(find_prime(1, 100))