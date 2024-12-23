from django.shortcuts import render, redirect
from .forms import ImageUploadForm
from .models import UploadedImage
from rembg import remove
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.http import HttpResponse
from PIL import Image, ImageDraw
import os

def home(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the original image
            uploaded_image = form.save()
            # Process background removal
            with uploaded_image.original_image.open("rb") as input_file:
                input_image = input_file.read()
                output = remove(input_image)

            # Save processed image to the model
            image = Image.open(BytesIO(output)).convert("RGBA")
            output_stream = BytesIO()
            image.save(output_stream, format="PNG")
            uploaded_image.processed_image.save("processed.png", ContentFile(output_stream.getvalue()))
            return redirect('edit_image', image_id=uploaded_image.id)
    else:
        form = ImageUploadForm()
    return render(request, 'home.html', {'form': form})

def edit_image(request, image_id):
    uploaded_image = UploadedImage.objects.get(id=image_id)

    if request.method == 'POST':
        # Get the selected color from the form (default is white)
        selected_color = request.POST.get("selected_color", "#FFFFFF")
        bg_color = tuple(int(selected_color[i:i+2], 16) for i in (1, 3, 5)) + (255,)  # RGB and full opacity

        # Load the processed image (which has its background removed)
        processed_image = Image.open(uploaded_image.processed_image).convert("RGBA")

        # Check if the user uploaded a background image
        background_image = request.FILES.get('background_image')

        if background_image:
            bg_img = Image.open(background_image).convert("RGBA")
            # Resize background image to the same size as the processed image
            bg_img = bg_img.resize(processed_image.size)
        else:
            bg_img = Image.new("RGBA", processed_image.size, bg_color)  # Solid color background

        # Combine the processed image on top of the background
        final_image = Image.alpha_composite(bg_img, processed_image)

        # Save the final image in memory
        output_stream = BytesIO()
        final_image.save(output_stream, format="PNG")
        output_stream.seek(0)

        # Prepare the response to send the image as a download
        response = HttpResponse(output_stream.read(), content_type="image/png")
        response['Content-Disposition'] = 'attachment; filename="edited_image.png"'

        return response

    return render(request, 'edit_image.html', {'image': uploaded_image})
