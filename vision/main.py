import argparse
import sys
import os
from pathlib import Path
import cv2
import torch
import numpy as np
from hydra import compose, initialize
from omegaconf import OmegaConf
from torchvision.transforms import functional as F

# Add yolo_repo to path
# Assuming main.py is in vision/ and yolo_repo is in vision/yolo_repo
REPO_PATH = Path(__file__).parent / "yolo_repo"
sys.path.append(str(REPO_PATH))

try:
    from yolo.model.yolo import create_model
    from yolo.utils.bounding_box_utils import create_converter
    from yolo.utils.model_utils import PostProcess
    from yolo.tools.drawer import draw_bboxes
except ImportError as e:
    print(f"Error importing YOLO modules: {e}")
    print(f"Make sure yolo_repo is cloned in {REPO_PATH}")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="YOLOv9 Inference App")
    parser.add_argument("--source", type=str, required=True, help="Path to image or video file, or '0' for webcam")
    parser.add_argument("--model", type=str, default="v9-c", help="Model name (e.g. v9-c)")
    parser.add_argument("--conf", type=float, default=0.25, help="Confidence threshold")
    parser.add_argument("--iou", type=float, default=0.45, help="IoU threshold")
    args = parser.parse_args()

    # Initialize Hydra and load config
    # We point to the config directory inside yolo_repo/yolo
    # We use a relative path from this script to the config folder
    config_dir = REPO_PATH / "yolo" / "config"
    
    # Hydra initialize expects a path relative to the calling python script or module
    # Since we are running this script, we can use relative path if we are careful.
    # But initialize works best with relative path to the caller.
    # Let's try to use the relative path from here.
    rel_config_path = os.path.relpath(config_dir, Path(__file__).parent)

    try:
        with initialize(version_base=None, config_path=rel_config_path):
            # Override model and nms settings
            overrides = [
                f"model={args.model}",
                "task=inference",
                f"task.nms.min_confidence={args.conf}",
                f"task.nms.min_iou={args.iou}",
                "use_wandb=False"
            ]
            cfg = compose(config_name="config", overrides=overrides)
    except Exception as e:
        print(f"Error initializing Hydra config: {e}")
        return

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # Load model
    print(f"Loading model {args.model}...")
    try:
        # weight_path=True triggers auto download
        model = create_model(cfg.model, weight_path=True, class_num=cfg.dataset.class_num)
        model = model.to(device)
        model.eval()
    except Exception as e:
        print(f"Error loading model: {e}")
        return
    
    # Create converter and post-process
    img_size = cfg.image_size if hasattr(cfg, "image_size") else [640, 640]
    if isinstance(img_size, int):
        img_size = [img_size, img_size]
    
    print(f"Model input size: {img_size}")

    converter = create_converter(cfg.model.name, model, cfg.model.anchor, img_size, device)
    nms_cfg = cfg.task.nms
    post_process = PostProcess(converter, nms_cfg)

    # Open source
    source = args.source
    if source.isdigit():
        source = int(source)
    
    cap = cv2.VideoCapture(source)
    
    if not cap.isOpened():
        print(f"Error opening source: {source}")
        return

    # Get class names if available (usually in dataset config)
    # cfg.dataset.class_list might be available
    class_names = cfg.dataset.class_list if hasattr(cfg.dataset, "class_list") else None

    print("Starting inference... Press 'q' to exit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Preprocess
        orig_h, orig_w = frame.shape[:2]
        
        # Resize to model input size
        # Note: Simple resize changes aspect ratio. 
        # For better results, use letterbox resizing (padding).
        # But for this simple app, we'll stick to resize and see.
        input_frame = cv2.resize(frame, (img_size[1], img_size[0]))
        
        # Convert to tensor
        # OpenCV is BGR, PyTorch usually expects RGB
        input_rgb = cv2.cvtColor(input_frame, cv2.COLOR_BGR2RGB)
        input_tensor = F.to_tensor(input_rgb).to(device)
        input_tensor = input_tensor.unsqueeze(0) # Add batch dim
        
        # Inference
        with torch.no_grad():
            outputs = model(input_tensor)
            # Post process
            # We pass image_size as the model input size
            bboxes = post_process(outputs, image_size=[img_size[1], img_size[0]])
            
        # bboxes is a list of tensors [class_id, x1, y1, x2, y2, conf]
        # Coordinates are in model input scale (img_size)
        
        # We need to scale bboxes back to original image size
        # Scale factors
        sx = orig_w / img_size[1]
        sy = orig_h / img_size[0]
        
        # We can draw on the original frame
        # But draw_bboxes expects normalized coordinates? 
        # Let's check draw_bboxes again.
        # "bboxes (List of Lists/Tensors): Bounding boxes with [class_id, x_min, y_min, x_max, y_max], where coordinates are normalized [0, 1]."
        # Wait, the docstring said normalized [0, 1].
        # But bbox_nms returns absolute coordinates in model scale?
        # Let's check bbox_nms again.
        # "pred_box[..., 0:2] = (pred_box[..., 0:2] * 2.0 - 0.5 + self.anchor_grids[layer_idx]) * self.strides[layer_idx]"
        # This looks like absolute coordinates (pixels).
        # And PostProcess calls converter which does this.
        
        # Let's check draw_bboxes implementation.
        # "class_id, x_min, y_min, x_max, y_max, *conf = [float(val) for val in bbox]"
        # "bbox = [(x_min, y_min), (x_max, y_max)]"
        # "draw.rounded_rectangle(bbox, ...)"
        # PIL draw takes pixel coordinates.
        # So draw_bboxes expects pixel coordinates!
        # The docstring might be misleading or referring to something else.
        # If it expects normalized, it would multiply by width/height. It doesn't seem to do that.
        
        # So bboxes are in pixels of img_size.
        # We need to scale them to orig_w, orig_h.
        
        current_bboxes = bboxes[0].cpu().clone()
        if len(current_bboxes) > 0:
            current_bboxes[:, 1] *= sx
            current_bboxes[:, 2] *= sy
            current_bboxes[:, 3] *= sx
            current_bboxes[:, 4] *= sy
        
        # Draw on original frame
        # draw_bboxes expects PIL or Tensor.
        # We can convert frame (numpy) to PIL
        frame_pil = F.to_pil_image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        
        drawn_pil = draw_bboxes(frame_pil, current_bboxes, idx2label=class_names)
        
        # Convert back to OpenCV
        drawn_cv2 = np.array(drawn_pil)
        drawn_cv2 = cv2.cvtColor(drawn_cv2, cv2.COLOR_RGB2BGR)
        
        cv2.imshow("YOLOv9 Inference", drawn_cv2)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
