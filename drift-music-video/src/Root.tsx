import { Composition } from 'remotion';
import { MusicVideoComposition } from './MusicVideoComposition';

// 2.39:1 Cinematic Widescreen at 24fps (4k resolution)
const WIDTH = 3840;
const HEIGHT = 1608;
const FPS = 24;

// Total duration: 3:30 minutes = 210 seconds = 5040 frames
const TOTAL_FRAMES = 210 * FPS;

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="DriftMusicVideo"
        component={MusicVideoComposition}
        durationInFrames={TOTAL_FRAMES}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
        defaultProps={{}}
      />
      
      {/* Preview composition for testing */}
      <Composition
        id="DriftScenePreview"
        component={MusicVideoComposition}
        durationInFrames={720}
        fps={FPS}
        width={1920}
        height={804}
      />
    </>
  );
};
