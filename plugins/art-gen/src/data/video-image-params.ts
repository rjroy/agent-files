export interface VideoParams {
  paramName: string;
  isArray: boolean;
}

export const VIDEO_PARAMS: Record<string, VideoParams> = {
  "wan-video/wan-2.2-i2v-fast": { paramName: "image", isArray: false },
  "minimax/video-01-live": { paramName: "first_frame_image", isArray: false },
  "pixverse/pixverse-v4": { paramName: "image", isArray: false },
  "minimax/hailuo-02": { paramName: "first_frame_image", isArray: false },
  "kwaivgi/kling-v2.5-turbo-pro": { paramName: "start_image", isArray: false },
  "kwaivgi/kling-v2.1-master": { paramName: "start_image", isArray: false },
};

export function getVideoParams(modelId: string): VideoParams {
  return VIDEO_PARAMS[modelId] ?? { paramName: "image", isArray: false };
}
