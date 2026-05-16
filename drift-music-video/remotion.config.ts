import { Config } from '@remotion/cli/config';

Config.setVideoImageFormat('jpeg');
Config.setOverwriteOutput(true);
Config.setConcurrency(8);

// Cinema quality settings
Config.setCodec('h264');
Config.setCrf(16);
Config.setPixelFormat('yuv420p');

export default Config;
