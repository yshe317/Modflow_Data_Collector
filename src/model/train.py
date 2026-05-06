import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import os
from unet import UNet


class SegmentationDataset(Dataset):
    def __init__(self, images_dir, masks_dir, transform=None):
        self.images_dir = images_dir
        self.masks_dir = masks_dir
        self.transform = transform
        self.image_files = [f for f in os.listdir(images_dir) if f.endswith('.png') or f.endswith('.jpg')]

    def __len__(self):
        return len(self.image_files)

    def __getitem__(self, idx):
        image_name = self.image_files[idx]
        mask_name = image_name.replace('.jpg', '.png').replace('.png', '_mask.png')

        image_path = os.path.join(self.images_dir, image_name)
        mask_path = os.path.join(self.masks_dir, mask_name)

        image = torch.load(image_path) if os.path.exists(image_path + '.pt') else torch.randn(1, 256, 256)
        mask = torch.load(mask_path) if os.path.exists(mask_path + '.pt') else torch.randn(1, 256, 256)

        if self.transform:
            image = self.transform(image)
            mask = self.transform(mask)

        return image, mask


class DiceLoss(nn.Module):
    def __init__(self, smooth=1e-6):
        super(DiceLoss, self).__init__()
        self.smooth = smooth

    def forward(self, pred, target):
        pred = torch.sigmoid(pred)
        pred_flat = pred.view(-1)
        target_flat = target.view(-1)
        intersection = (pred_flat * target_flat).sum()
        dice = (2. * intersection + self.smooth) / (pred_flat.sum() + target_flat.sum() + self.smooth)
        return 1 - dice


class CombinedLoss(nn.Module):
    def __init__(self):
        super(CombinedLoss, self).__init__()
        self.bce = nn.BCEWithLogitsLoss()
        self.dice = DiceLoss()

    def forward(self, pred, target):
        return self.bce(pred, target) + self.dice(pred, target)


def calculate_metrics(pred, target, threshold=0.5):
    pred = torch.sigmoid(pred) > threshold
    target = target > threshold

    pred_flat = pred.view(-1).float()
    target_flat = target.view(-1).float()

    tp = (pred_flat * target_flat).sum().item()
    fp = (pred_flat * (1 - target_flat)).sum().item()
    fn = ((1 - pred_flat) * target_flat).sum().item()
    tn = ((1 - pred_flat) * (1 - target_flat)).sum().item()

    precision = tp / (tp + fp + 1e-6)
    recall = tp / (tp + fn + 1e-6)
    f1 = 2 * precision * recall / (precision + recall + 1e-6)
    accuracy = (tp + tn) / (tp + tn + fp + fn + 1e-6)
    iou = tp / (tp + fp + fn + 1e-6)

    return {
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'accuracy': accuracy,
        'iou': iou
    }


def train_one_epoch(model, dataloader, criterion, optimizer, device):
    model.train()
    running_loss = 0.0
    running_metrics = {'precision': 0, 'recall': 0, 'f1': 0, 'accuracy': 0, 'iou': 0}

    for images, masks in dataloader:
        images = images.to(device)
        masks = masks.to(device)

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, masks)
        loss.backward()
        optimizer.step()

        running_loss += loss.item()
        metrics = calculate_metrics(outputs, masks)
        for key in running_metrics:
            running_metrics[key] += metrics[key]

    epoch_loss = running_loss / len(dataloader)
    epoch_metrics = {k: v / len(dataloader) for k, v in running_metrics.items()}

    return epoch_loss, epoch_metrics


def validate_one_epoch(model, dataloader, criterion, device):
    model.eval()
    running_loss = 0.0
    running_metrics = {'precision': 0, 'recall': 0, 'f1': 0, 'accuracy': 0, 'iou': 0}

    with torch.no_grad():
        for images, masks in dataloader:
            images = images.to(device)
            masks = masks.to(device)

            outputs = model(images)
            loss = criterion(outputs, masks)

            running_loss += loss.item()
            metrics = calculate_metrics(outputs, masks)
            for key in running_metrics:
                running_metrics[key] += metrics[key]

    epoch_loss = running_loss / len(dataloader)
    epoch_metrics = {k: v / len(dataloader) for k, v in running_metrics.items()}

    return epoch_loss, epoch_metrics


def train_model(model, train_loader, val_loader, criterion, optimizer, scheduler, num_epochs, device, save_path):
    best_iou = 0.0

    for epoch in range(num_epochs):
        print(f'Epoch {epoch + 1}/{num_epochs}')
        print('-' * 50)

        train_loss, train_metrics = train_one_epoch(model, train_loader, criterion, optimizer, device)
        print(f'Train Loss: {train_loss:.4f} | Train IoU: {train_metrics["iou"]:.4f}')

        val_loss, val_metrics = validate_one_epoch(model, val_loader, criterion, device)
        print(f'Val Loss: {val_loss:.4f} | Val IoU: {val_metrics["iou"]:.4f}')

        if scheduler:
            scheduler.step()

        if val_metrics['iou'] > best_iou:
            best_iou = val_metrics['iou']
            torch.save(model.state_dict(), save_path)
            print(f'Model saved with IoU: {best_iou:.4f}')

        print()

    return model


def main():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f'Using device: {device}')

    model = UNet(n_channels=1, n_classes=1, bilinear=True).to(device)

    train_images_dir = 'data/train/images'
    train_masks_dir = 'data/train/masks'
    val_images_dir = 'data/val/images'
    val_masks_dir = 'data/val/masks'

    train_dataset = SegmentationDataset(train_images_dir, train_masks_dir)
    val_dataset = SegmentationDataset(val_images_dir, val_masks_dir)

    train_loader = DataLoader(train_dataset, batch_size=4, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=4, shuffle=False, num_workers=0)

    criterion = CombinedLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.5)

    num_epochs = 50
    save_path = 'checkpoints/unet_best.pth'

    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    model = train_model(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        criterion=criterion,
        optimizer=optimizer,
        scheduler=scheduler,
        num_epochs=num_epochs,
        device=device,
        save_path=save_path
    )

    print('Training completed!')


if __name__ == '__main__':
    main()