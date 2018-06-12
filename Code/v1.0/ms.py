from hc import HC


def ms(devices):
    x = HC(devices)
    x.get_delta_list()
    x.run(5)

