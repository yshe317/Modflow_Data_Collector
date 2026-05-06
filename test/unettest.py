import torch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'model'))

from unet import UNet, DoubleConv, Down, Up, OutConv


def test_unet_creation():
    print("Test 1: UNet model creation...")
    model = UNet(n_channels=1, n_classes=1)
    assert model is not None
    print("PASSED: Model created successfully")


def test_unet_forward():
    print("\nTest 2: UNet forward pass...")
    model = UNet(n_channels=1, n_classes=1)
    batch_size = 2
    height, width = 256, 256
    x = torch.randn(batch_size, 1, height, width)

    output = model(x)

    assert output.shape == (batch_size, 1, height, width), \
        f"Expected shape ({batch_size}, 1, {height}, {width}), got {output.shape}"
    print(f"PASSED: Output shape is correct: {output.shape}")


def test_unet_multiclass():
    print("\nTest 3: UNet with multiple classes...")
    model = UNet(n_channels=3, n_classes=5)
    x = torch.randn(1, 3, 128, 128)

    output = model(x)

    assert output.shape == (1, 5, 128, 128)
    print(f"PASSED: Multiclass output shape is correct: {output.shape}")


def test_unet_different_sizes():
    print("\nTest 4: UNet with different input sizes...")
    model = UNet(n_channels=1, n_classes=1)
    sizes = [(128, 128), (256, 256), (512, 512)]

    for h, w in sizes:
        x = torch.randn(1, 1, h, w)
        output = model(x)
        assert output.shape == (1, 1, h, w), \
            f"Failed for input size ({h}, {w})"
    print("PASSED: All input sizes work correctly")


def test_double_conv():
    print("\nTest 5: DoubleConv layer...")
    layer = DoubleConv(in_channels=64, out_channels=128)
    x = torch.randn(1, 64, 64, 64)

    output = layer(x)

    assert output.shape == (1, 128, 64, 64)
    print("PASSED: DoubleConv output shape is correct")


def test_down_layer():
    print("\nTest 6: Down (MaxPool + DoubleConv) layer...")
    layer = Down(in_channels=64, out_channels=128)
    x = torch.randn(1, 64, 64, 64)

    output = layer(x)

    assert output.shape == (1, 128, 32, 32)
    print("PASSED: Down layer halves spatial dimensions")


def test_up_layer():
    print("\nTest 7: Up layer with skip connection...")
    layer = Up(in_channels=512, out_channels=256)
    x1 = torch.randn(1, 256, 32, 32)
    x2 = torch.randn(1, 256, 64, 64)

    output = layer(x1, x2)

    assert output.shape == (1, 256, 64, 64)
    print("PASSED: Up layer correctly handles skip connections")


def test_out_conv():
    print("\nTest 8: OutConv (1x1 convolution) layer...")
    layer = OutConv(in_channels=64, out_channels=1)
    x = torch.randn(1, 64, 128, 128)

    output = layer(x)

    assert output.shape == (1, 1, 128, 128)
    print("PASSED: OutConv correctly reduces channels to num_classes")


def test_model_parameters():
    print("\nTest 9: Model parameter count...")
    model = UNet(n_channels=1, n_classes=1)
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)

    print(f"Total parameters: {total_params:,}")
    print(f"Trainable parameters: {trainable_params:,}")
    assert trainable_params > 0
    print("PASSED: Model has trainable parameters")


def test_no_bias_in_main_layers():
    print("\nTest 10: Encoder/Decoder Conv layers have no bias before BatchNorm...")
    model = UNet(n_channels=1, n_classes=1)

    has_conv_bias = False
    for name, m in model.named_modules():
        if isinstance(m, nn.Conv2d) and 'outc' not in name:
            if m.bias is not None:
                has_conv_bias = True
                print(f"Found Conv2d with bias: {name}")
                break

    assert not has_conv_bias, "Found Conv2d with bias before BatchNorm in main layers"
    print("PASSED: Main layers have no bias before BatchNorm")


def test_gradients():
    print("\nTest 11: Gradients flow through model...")
    model = UNet(n_channels=1, n_classes=1)
    x = torch.randn(1, 1, 64, 64)
    target = torch.randn(1, 1, 64, 64)

    output = model(x)
    loss = torch.nn.functional.mse_loss(output, target)
    loss.backward()

    has_grad = all(p.grad is not None for p in model.parameters() if p.requires_grad)
    assert has_grad
    print("PASSED: Gradients flow correctly through all layers")


def test_eval_mode():
    print("\nTest 12: Model in eval mode...")
    model = UNet(n_channels=1, n_classes=1)
    model.eval()

    x = torch.randn(1, 1, 128, 128)
    with torch.no_grad():
        output1 = model(x)
        output2 = model(x)

    assert torch.allclose(output1, output2)
    print("PASSED: Model produces deterministic output in eval mode")


def test_bilinear_vs_transposed():
    print("\nTest 13: Bilinear upsampling vs Transposed Convolution...")
    model_bilinear = UNet(n_channels=1, n_classes=1, bilinear=True)
    model_transposed = UNet(n_channels=1, n_classes=1, bilinear=False)

    x = torch.randn(1, 1, 64, 64)

    out_bilinear = model_bilinear(x)
    out_transposed = model_transposed(x)

    assert out_bilinear.shape == out_transposed.shape
    print(f"PASSED: Both modes produce same output shape: {out_bilinear.shape}")


if __name__ == '__main__':
    import torch.nn as nn

    print("=" * 60)
    print("UNet Model Tests")
    print("=" * 60)

    test_unet_creation()
    test_unet_forward()
    test_unet_multiclass()
    test_unet_different_sizes()
    test_double_conv()
    test_down_layer()
    test_up_layer()
    test_out_conv()
    test_model_parameters()
    test_no_bias_in_main_layers()
    test_gradients()
    test_eval_mode()
    test_bilinear_vs_transposed()

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED!")
    print("=" * 60)