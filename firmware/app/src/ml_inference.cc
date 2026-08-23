#include "ml_inference.h"

#include <math.h>
#include <stdint.h>

#include "zephyr/kernel.h"
#include "zephyr/sys/printk.h"

#include "model_data.h"

#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/micro/micro_mutable_op_resolver.h"
#include "tensorflow/lite/schema/schema_generated.h"

namespace {

constexpr size_t kTensorArenaSize = 16 * 1024;
alignas(16) uint8_t tensor_arena[kTensorArenaSize];

const tflite::Model* model = nullptr;
tflite::MicroInterpreter* interpreter = nullptr;
TfLiteTensor* input_tensor = nullptr;
TfLiteTensor* output_tensor = nullptr;

tflite::MicroMutableOpResolver<2> resolver;

bool initialized = false;

}  // namespace

extern "C" int ml_inference_init(void)
{
    printk("Aegis ML: initializing TFLM...\n");

    model = tflite::GetModel(aegis_fault_model_int8_tflite);

    if (model == nullptr) {
        printk("Aegis ML: failed to load model\n");
        return -1;
    }

    if (model->version() != TFLITE_SCHEMA_VERSION) {
        printk("Aegis ML: schema mismatch: model=%d runtime=%d\n",
               model->version(),
               TFLITE_SCHEMA_VERSION);
        return -2;
    }

    if (resolver.AddFullyConnected() != kTfLiteOk) {
        printk("Aegis ML: failed to register FullyConnected\n");
        return -3;
    }

    if (resolver.AddSoftmax() != kTfLiteOk) {
        printk("Aegis ML: failed to register Softmax\n");
        return -4;
    }

    static tflite::MicroInterpreter static_interpreter(
        model,
        resolver,
        tensor_arena,
        kTensorArenaSize);

    interpreter = &static_interpreter;

    if (interpreter->AllocateTensors() != kTfLiteOk) {
        printk("Aegis ML: AllocateTensors() failed\n");
        return -5;
    }

    input_tensor = interpreter->input(0);
    output_tensor = interpreter->output(0);

    if (input_tensor == nullptr || output_tensor == nullptr) {
        printk("Aegis ML: invalid input/output tensor\n");
        return -6;
    }

    printk("Aegis ML: initialized successfully\n");

    printk("Aegis ML: input type=%d shape=[%d,%d]\n",
           input_tensor->type,
           input_tensor->dims->data[0],
           input_tensor->dims->data[1]);

    printk("Aegis ML: input scale=%f zero_point=%d\n",
           (double)input_tensor->params.scale,
           input_tensor->params.zero_point);

    printk("Aegis ML: output type=%d shape=[%d,%d]\n",
           output_tensor->type,
           output_tensor->dims->data[0],
           output_tensor->dims->data[1]);

    printk("Aegis ML: output scale=%f zero_point=%d\n",
           (double)output_tensor->params.scale,
           output_tensor->params.zero_point);

    initialized = true;

    return 0;
}

extern "C" ml_fault_t ml_predict(
    float temperature,
    float voltage,
    float rpm)
{
    if (!initialized) {
        printk("Aegis ML: not initialized\n");
        return ML_FAULT_NORMAL;
    }

    /*
     * The model was trained with the three input features rescaled to
     * approximately [0, 1].
     *
     * Feature scales:
     *   temperature -> 100
     *   voltage     -> 4
     *   rpm         -> 5000
     */

    const float features[3] = {
        temperature / 100.0f,
        voltage / 4.0f,
        rpm / 5000.0f
    };

    const float input_scale = 0.003918295726180077f;
    const int input_zero_point = -128;

    for (int i = 0; i < 3; ++i) {

        const float division = features[i] / input_scale;
        const float rounded = roundf(division);

        const int32_t quantized =
            static_cast<int32_t>(rounded) + input_zero_point;

        int32_t clamped = quantized;

        if (clamped > 127) {
            clamped = 127;
        } else if (clamped < -128) {
            clamped = -128;
        }

        input_tensor->data.int8[i] =
            static_cast<int8_t>(clamped);

    }

    if (interpreter->Invoke() != kTfLiteOk) {
        printk("Aegis ML: Invoke() failed\n");
        return ML_FAULT_NORMAL;
    }


    int best_index = 0;
    int8_t best_value = output_tensor->data.int8[0];

    for (int i = 1; i < 4; ++i) {
        if (output_tensor->data.int8[i] > best_value) {
            best_value = output_tensor->data.int8[i];
            best_index = i;
        }
    }

    return static_cast<ml_fault_t>(best_index);
}
