import tensorflow as tf

# Kiểm tra GPU trong TF2 mode
print("GPU Available (TF2 mode):", tf.test.is_gpu_available())
print("GPU Devices (TF2 mode):", tf.config.list_physical_devices('GPU'))

# Chuyển sang TF1 compat mode
tf.compat.v1.disable_v2_behavior()
config = tf.compat.v1.ConfigProto(
    gpu_options=tf.compat.v1.GPUOptions(allow_growth=True),
    allow_soft_placement=True,
    log_device_placement=True
)
with tf.compat.v1.Session(config=config) as sess:
    print("GPU Available (TF1 mode):", tf.test.is_gpu_available())
    print("GPU Devices (TF1 mode):", tf.config.list_physical_devices('GPU'))