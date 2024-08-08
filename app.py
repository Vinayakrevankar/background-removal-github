import gradio as gr
from gradio_imageslider import ImageSlider
from loadimg import load_img
import spaces
from transformers import AutoModelForImageSegmentation
import torch
from torchvision import transforms

# torch.set_float32_matmul_precision(['high', 'highest'][0])

birefnet = AutoModelForImageSegmentation.from_pretrained('zhengpeng7/BiRefNet', trust_remote_code=True,torch_dtype=torch.float16)
birefnet.to("cuda")
transform_image = transforms.Compose([
    transforms.Resize((1024, 1024)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])



@spaces.GPU
def fn(image):
    im = load_img(image)
    im = im.convert('RGB') 
    image = load_img(im)
    input_images = transform_image(image).unsqueeze(0).to('cuda')
    # Prediction
    with torch.no_grad():
        preds = birefnet(input_images)[-1].sigmoid().cpu()
    pred = preds[0].squeeze()
    pred_pil = transforms.ToPILImage()(pred)
    out = (pred_pil , im)
    return out

slider1 = ImageSlider(label="birefnet", type="pil")
slider2 = ImageSlider(label="birefnet", type="pil")
image = gr.Image(label="Upload an image")
text = gr.Textbox(label="Paste an image URL")


tab1 = gr.Interface(fn,inputs= image, outputs= slider1, api_name="image")
tab2 = gr.Interface(fn,inputs= text, outputs= slider2, api_name="text")

demo = gr.TabbedInterface([tab1,tab2],["image","text"],title="birefnet with image slider")

if __name__ == "__main__":
    demo.launch()