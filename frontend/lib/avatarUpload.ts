const MAX_BYTES = 2 * 1024 * 1024;
const TARGET_SIZE = 512;

export async function prepareAvatarFile(
  file: File,
  rotationDegrees = 0,
): Promise<Blob> {
  const bitmap = await createImageBitmap(file);
  try {
    const normalizedDegrees = ((rotationDegrees % 360) + 360) % 360;
    const rotatedCanvas = drawRotatedBitmap(bitmap, normalizedDegrees);
    const crop = cropSquareDimensions(rotatedCanvas.width, rotatedCanvas.height);

    const canvas = document.createElement("canvas");
    canvas.width = TARGET_SIZE;
    canvas.height = TARGET_SIZE;
    const ctx = canvas.getContext("2d");
    if (!ctx) throw new Error("Could not prepare image");

    ctx.drawImage(
      rotatedCanvas,
      crop.x,
      crop.y,
      crop.w,
      crop.h,
      0,
      0,
      TARGET_SIZE,
      TARGET_SIZE,
    );

    let quality = 0.9;
    let blob = await canvasToBlob(canvas, quality);
    while (blob.size > MAX_BYTES && quality > 0.2) {
      quality -= 0.1;
      blob = await canvasToBlob(canvas, quality);
    }
    if (blob.size > MAX_BYTES) {
      throw new Error("Image is too large. Choose a smaller photo.");
    }
    return blob;
  } finally {
    bitmap.close();
  }
}

function drawRotatedBitmap(bitmap: ImageBitmap, degrees: number): HTMLCanvasElement {
  const canvas = document.createElement("canvas");
  const ctx = canvas.getContext("2d");
  if (!ctx) throw new Error("Could not prepare image");

  if (degrees === 0) {
    canvas.width = bitmap.width;
    canvas.height = bitmap.height;
    ctx.drawImage(bitmap, 0, 0);
    return canvas;
  }

  const radians = (degrees * Math.PI) / 180;
  const sin = Math.abs(Math.sin(radians));
  const cos = Math.abs(Math.cos(radians));
  canvas.width = Math.floor(bitmap.width * cos + bitmap.height * sin);
  canvas.height = Math.floor(bitmap.width * sin + bitmap.height * cos);

  ctx.translate(canvas.width / 2, canvas.height / 2);
  ctx.rotate(radians);
  ctx.drawImage(bitmap, -bitmap.width / 2, -bitmap.height / 2);
  return canvas;
}

function cropSquareDimensions(
  sourceWidth: number,
  sourceHeight: number,
): { x: number; y: number; w: number; h: number } {
  const targetAspect = 1;
  const sourceAspect = sourceWidth / sourceHeight;
  if (sourceAspect > targetAspect) {
    const h = sourceHeight;
    const w = Math.round(h * targetAspect);
    return { x: Math.round((sourceWidth - w) / 2), y: 0, w, h };
  }
  const w = sourceWidth;
  const h = Math.round(w / targetAspect);
  return { x: 0, y: Math.round((sourceHeight - h) / 2), w, h };
}

function canvasToBlob(canvas: HTMLCanvasElement, quality: number): Promise<Blob> {
  return new Promise((resolve, reject) => {
    canvas.toBlob(
      (blob) => (blob ? resolve(blob) : reject(new Error("Could not encode image"))),
      "image/jpeg",
      quality,
    );
  });
}
