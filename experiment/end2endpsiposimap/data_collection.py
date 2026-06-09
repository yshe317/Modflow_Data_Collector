from test.base import get_model

def main():
    model = get_model()

    model.forward([[70,70,0.1,100,0, 10]])
    model.collect("scenarios/base/ksep.tif", savepath = "e2e-001")
    

    model.forward([[70,130,0.1,100,0, 10]])
    model.collect("scenarios/base/ksep.tif",savepath = "e2e-002")