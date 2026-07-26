export interface Img2ImgParams {
  paramName: string;
  isArray: boolean;
  strengthParam: string | null;
}

export const IMG2IMG_PARAMS: Record<string, Img2ImgParams> = {
  "black-forest-labs/flux-2-pro": { paramName: "input_images", isArray: true, strengthParam: null },
  "google/nano-banana-pro": { paramName: "image_input", isArray: true, strengthParam: null },
  "prunaai/p-image-edit": { paramName: "images", isArray: true, strengthParam: null },
  "stability-ai/stable-diffusion-img2img": { paramName: "image", isArray: false, strengthParam: "prompt_strength" },
};

export function getImg2ImgParams(modelId: string): Img2ImgParams {
  return IMG2IMG_PARAMS[modelId] ?? { paramName: "image", isArray: false, strengthParam: null };
}
