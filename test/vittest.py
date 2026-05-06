import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch
from src.model.vit import ViT


def test_vit_initialization():
    print("Testing ViT initialization...")
    
    model = ViT(
        image_size=32,
        patch_size=4,
        num_classes=10,
        dim=128,
        depth=3,
        heads=4,
        mlp_dim=256,
        dropout=0.1,
        emb_dropout=0.1
    )
    
    print("[OK] ViT model initialized successfully")
    return model


def test_vit_forward_pass():
    print("\nTesting ViT forward pass...")
    
    model = ViT(
        image_size=32,
        patch_size=4,
        num_classes=10,
        dim=128,
        depth=3,
        heads=4,
        mlp_dim=256,
        dropout=0.1,
        emb_dropout=0.1
    )
    
    batch_size = 2
    dummy_input = torch.randn(batch_size, 3, 32, 32)
    
    with torch.no_grad():
        output = model(dummy_input)
    
    assert output.shape == (batch_size, 10), f"Expected output shape (2, 10), got {output.shape}"
    print(f"[OK] Forward pass successful, output shape: {output.shape}")
    return output


def test_vit_without_mlp_head():
    print("\nTesting ViT without MLP head...")
    
    model = ViT(
        image_size=32,
        patch_size=4,
        num_classes=0,
        dim=128,
        depth=3,
        heads=4,
        mlp_dim=256,
        dropout=0.1,
        emb_dropout=0.1,
        pool='cls'
    )
    
    batch_size = 2
    dummy_input = torch.randn(batch_size, 3, 32, 32)
    
    with torch.no_grad():
        output = model(dummy_input)
    
    num_patches = (32 // 4) * (32 // 4)
    expected_shape = (batch_size, num_patches + 1, 128)
    assert output.shape == expected_shape, f"Expected output shape {expected_shape}, got {output.shape}"
    print(f"[OK] ViT without MLP head works, output shape: {output.shape}")
    return output


def test_vit_mean_pooling():
    print("\nTesting ViT with mean pooling...")
    
    model = ViT(
        image_size=32,
        patch_size=4,
        num_classes=10,
        dim=128,
        depth=3,
        heads=4,
        mlp_dim=256,
        dropout=0.1,
        emb_dropout=0.1,
        pool='mean'
    )
    
    batch_size = 2
    dummy_input = torch.randn(batch_size, 3, 32, 32)
    
    with torch.no_grad():
        output = model(dummy_input)
    
    assert output.shape == (batch_size, 10), f"Expected output shape (2, 10), got {output.shape}"
    print(f"[OK] Mean pooling works, output shape: {output.shape}")
    return output


def test_vit_different_sizes():
    print("\nTesting ViT with different image and patch sizes...")
    
    # Test with 64x64 images and 8x8 patches
    model = ViT(
        image_size=64,
        patch_size=8,
        num_classes=5,
        dim=64,
        depth=2,
        heads=2,
        mlp_dim=128,
        channels=1
    )
    
    batch_size = 1
    dummy_input = torch.randn(batch_size, 1, 64, 64)
    
    with torch.no_grad():
        output = model(dummy_input)
    
    assert output.shape == (batch_size, 5), f"Expected output shape (1, 5), got {output.shape}"
    print(f"[OK] Different sizes work, output shape: {output.shape}")
    return output


def run_all_tests():
    print("=" * 50)
    print("Running ViT Model Tests")
    print("=" * 50)
    
    try:
        test_vit_initialization()
        test_vit_forward_pass()
        test_vit_without_mlp_head()
        test_vit_mean_pooling()
        test_vit_different_sizes()
        
        print("\n" + "=" * 50)
        print("[OK] All tests passed!")
        print("=" * 50)
    except Exception as e:
        print("\n" + "=" * 50)
        print(f"[FAIL] Test failed: {e}")
        print("=" * 50)
        raise


if __name__ == "__main__":
    run_all_tests()
