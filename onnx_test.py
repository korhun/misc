import time
import onnxruntime as rt

# onnx_fn = "C:/_koray/netcadlabs/ndu-gate/runners/yolov5m/data/yolov5m.onnx"

# onnx_fn ="C:/_koray/temp/yolov5m.onnx"
# onnx_fn ="C:/_koray/temp/Model.onnx"

# https://onnxzoo.blob.core.windows.net/models/opset_10/ssd/ssd.onnx
onnx_fn ="C:/_koray/temp/ssd.onnx"

for i in range(100):
    start = time.time()
    sess = rt.InferenceSession(onnx_fn)
    elapsed = time.time() - start
    print(f"InferenceSession: {elapsed:.0f}sec")

    input_name = sess.get_inputs()[0].name
    # print("input name", input_name)
    # input_shape = sess.get_inputs()[0].shape
    # print("input shape", input_shape)
    # input_type = sess.get_inputs()[0].type
    # print("input type", input_type)

    output_name = sess.get_outputs()[0].name
    # print("output name", output_name)
    # output_shape = sess.get_outputs()[0].shape
    # print("output shape", output_shape)
    # output_type = sess.get_outputs()[0].type
    # print("output type", output_type)

    import numpy.random

    x = numpy.random.random((1, 3, 1200, 1200))
    x = x.astype(numpy.float32)

    start = time.time()
    res = sess.run([output_name], {input_name: x})
    elapsed = time.time() - start
    print(f"sess.run: {elapsed:.0f}sec")

    # print(res)
