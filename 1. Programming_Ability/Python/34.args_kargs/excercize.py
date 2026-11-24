# excercize

def shipping_lable(*args, **kargs):
    for arg in args:
        print(arg, end=" ")
    print()

    if "apt" in kargs:
        print(f"{kargs.get('street')}")
        print(f"{kargs.get('apt')} {kargs.get('number')}")
    elif "pobox" in kargs:
        print(f"{kargs.get('street')}")
        print(f"{kargs.get('pobox')} {kargs.get('number')}")
    else:
        print(f"{kargs.get('street')}")
        print(f"{kargs.get('number')}")

shipping_lable("Dr.", "SpongeBob", "Harold", "Squarepants",
               street="8739 Unknown St.", 
               pobox="#1002",
               city="ShangHai",
               number=100,
               apt="#2001")