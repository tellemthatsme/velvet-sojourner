import { useCurrentFrame, useVideoConfig, interpolate, spring, AbsoluteFill, Img, Audio, Sequence } from 'remotion';
import { TransitionSeries } from '@remotion/transitions';
import { fade } from '@remotion/transitions/fade';
import { slide } from '@remotion/transitions/slide';

const neonPurple = '#9933ff';
const neonBlue = '#00ccff';
const neonPink = '#ff33cc';
const neonCyan = '#00ffff';

// Drift video scene configuration
const scenes = [
  { id: 'intro', start: 0, duration: 720, color: neonPurple, title: 'MIDNIGHT DRIFT' },
  { id: 'verse1', start: 720, duration: 720, color: '#ff6600', title: 'ENGINE START' },
  { id: 'chorus', start: 1440, duration: 1080, color: neonPink, title: 'FULL THROTTLE' },
  { id: 'verse2', start: 2520, duration: 720, color: '#00ff66', title: 'STREET MEET' },
  { id: 'bridge', start: 3240, duration: 720, color: neonPurple, title: 'OVERLOOK' },
  { id: 'outro', start: 3960, duration: 720, color: '#ffcc00', title: 'SUNRISE' },
];

const LightTrail: React.FC<{ x: number; y: number; delay: number }> = ({ x, y, delay }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  
  const progress = spring({
    frame: frame - delay,
    fps,
    config: { damping: 12, stiffness: 80 },
  });
  
  const opacity = interpolate(progress, [0, 0.5, 1], [0, 1, 0]);
  const scale = interpolate(progress, [0, 1], [0.8, 2.5]);
  
  return (
    <div
      style={{
        position: 'absolute',
        left: x,
        top: y,
        width: 300,
        height: 4,
        background: `linear-gradient(90deg, transparent, ${neonCyan}, transparent)`,
        transform: `scaleX(${scale})`,
        opacity,
        filter: 'blur(2px)',
      }}
    />
  );
};

const NeonGlow: React.FC<{ color: string; intensity: number }> = ({ color, intensity }) => {
  const frame = useCurrentFrame();
  const flicker = Math.sin(frame * 0.1) * 0.1 + 0.9;
  
  return (
    <div
      style={{
        position: 'absolute',
        inset: 0,
        background: `radial-gradient(ellipse at center, ${color}${Math.floor(intensity * flicker * 30).toString(16).padStart(2, '0')} 0%, transparent 70%)`,
        pointerEvents: 'none',
      }}
    />
  );
};

const DriftCarScene: React.FC<{ sceneId: string; color: string }> = ({ sceneId, color }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  
  const carX = interpolate(frame, [0, 60], [width + 200, width * 0.3], {
    extrapolateRight: 'clamp',
  });
  
  const driftAngle = spring({
    frame,
    fps,
    config: { damping: 8, stiffness: 60 },
    delay: 15,
  }) * 25 - 12;
  
  const smokeOpacity = interpolate(frame, [20, 40], [0, 0.7], {
    extrapolateRight: 'clamp',
  });
  
  return (
    <AbsoluteFill style={{ backgroundColor: '#0a0a0f' }}>
      {/* City background */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: 'linear-gradient(180deg, #0f0f2a 0%, #000000 100%)',
        }}
      />
      
      {/* Building silhouettes */}
      {Array.from({ length: 15 }).map((_, i) => (
        <div
          key={i}
          style={{
            position: 'absolute',
            bottom: 0,
            left: `${i * 7}%`,
            width: 80 + i * 12,
            height: 200 + Math.sin(i * 0.8) * 150,
            backgroundColor: '#111118',
            opacity: 0.9,
          }}
        />
      ))}
      
      {/* Neon signs */}
      {Array.from({ length: 8 }).map((_, i) => (
        <div
          key={`neon-${i}`}
          style={{
            position: 'absolute',
            left: `${10 + i * 12}%`,
            top: `${10 + (i % 3) * 15}%`,
            width: 4 + (i % 3),
            height: 60 + i * 10,
            backgroundColor: [neonPurple, neonPink, neonBlue, neonCyan][i % 4],
            filter: 'blur(4px)',
            opacity: Math.sin(frame * 0.05 + i) > 0 ? 0.8 : 0.6,
          }}
        />
      ))}
      
      {/* Drifting car silhouette */}
      <div
        style={{
          position: 'absolute',
          left: carX,
          top: height * 0.65,
          width: 400,
          height: 120,
          transform: `rotate(${driftAngle}deg)`,
          transformOrigin: 'center bottom',
        }}
      >
        <svg viewBox="0 0 400 120" style={{ width: '100%', height: '100%' }}>
          <path
            d="M 80 90 L 100 50 L 150 40 L 250 40 L 320 50 L 350 70 L 370 90 Z"
            fill="#111111"
            stroke={color}
            strokeWidth="3"
          />
          <circle cx="130" cy="90" r="35" fill="#222" stroke={color} strokeWidth="2" />
          <circle cx="320" cy="90" r="35" fill="#222" stroke={color} strokeWidth="2" />
          <rect x="120" y="35" width="160" height="30" fill="#050510" stroke={color} strokeWidth="1" />
          
          {/* Headlights */}
          <circle cx="370" cy="75" r="8" fill={color} style={{ filter: 'blur(6px)' }} />
          <circle cx="370" cy="75" r="4" fill="white" />
          
          {/* Taillights */}
          <rect x="60" y="65" width="15" height="10" fill="#ff0000" style={{ filter: 'blur(3px)' }} />
        </svg>
      </div>
      
      {/* Drift smoke */}
      <div
        style={{
          position: 'absolute',
          left: carX - 100,
          top: height * 0.7,
          width: 300,
          height: 150,
          borderRadius: '50%',
          background: 'radial-gradient(ellipse, rgba(200,200,200,0.6) 0%, transparent 70%)',
          opacity: smokeOpacity,
          filter: 'blur(20px)',
          transform: `translateX(${frame * 2}px)`,
        }}
      />
      
      {/* Light trails */}
      <LightTrail x={width * 0.2} y={height * 0.5} delay={0} />
      <LightTrail x={width * 0.5} y={height * 0.4} delay={20} />
      <LightTrail x={width * 0.7} y={height * 0.6} delay={40} />
      
      {/* Vignette */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          boxShadow: 'inset 0 0 150px 80px rgba(0,0,0,0.9)',
          pointerEvents: 'none',
        }}
      />
      
      {/* Chromatic aberration effect */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          mixBlendMode: 'screen',
          background: `linear-gradient(45deg, ${neonPurple}22, transparent, ${neonCyan}22)`,
          opacity: 0.15,
        }}
      />
      
      <NeonGlow color={color} intensity={0.4} />
      
      {/* Scene title overlay */}
      <div
        style={{
          position: 'absolute',
          bottom: 100,
          left: 80,
          fontFamily: 'Inter, sans-serif',
          color: 'white',
          fontSize: 48,
          fontWeight: 900,
          letterSpacing: 6,
          textTransform: 'uppercase',
          textShadow: `0 0 30px ${color}, 0 0 60px ${color}`,
          opacity: interpolate(frame, [0, 30, 60], [0, 1, 0.9]),
        }}
      >
        {sceneId.toUpperCase()}
      </div>
    </AbsoluteFill>
  );
};

const SingerOverlay: React.FC = () => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  
  const opacity = interpolate(frame, [0, 40, 600, 640], [0, 0.85, 0.85, 0]);
  const xPos = width * 0.7 + Math.sin(frame * 0.02) * 10;
  
  return (
    <div
      style={{
        position: 'absolute',
        right: 60,
        bottom: 80,
        width: 320,
        height: 400,
        borderRadius: 12,
        border: `3px solid ${neonCyan}`,
        boxShadow: `0 0 40px ${neonCyan}66, inset 0 0 20px ${neonCyan}22`,
        overflow: 'hidden',
        opacity,
        transform: `translateX(${Math.sin(frame * 0.015) * 5}px)`,
        background: 'linear-gradient(180deg, #0a0a1a 0%, #000000 100%)',
      }}
    >
      {/* Placeholder for your image - replace with actual */}
      <div
        style={{
          width: '100%',
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontFamily: 'Inter, sans-serif',
          color: neonCyan,
          fontSize: 20,
          letterSpacing: 4,
        }}
      >
        YOUR IMAGE HERE
      </div>
      
      <div
        style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0,
          height: 60,
          background: 'linear-gradient(180deg, transparent, rgba(0,0,0,0.9))',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: 14,
          letterSpacing: 3,
          color: 'white',
          textTransform: 'uppercase',
        }}
      >
        TELLEMTHATSME
      </div>
    </div>
  );
};

export const MusicVideoComposition: React.FC = () => {
  const { fps, width, height } = useVideoConfig();
  
  return (
    <AbsoluteFill>
      <TransitionSeries>
        {scenes.map((scene, index) => (
          <TransitionSeries.Sequence
            key={scene.id}
            durationInFrames={scene.duration}
          >
            <DriftCarScene sceneId={scene.id} color={scene.color} />
            
            {/* Add singer overlay during chorus and verses */}
            {['verse1', 'chorus', 'verse2'].includes(scene.id) && (
              <Sequence from={30} durationInFrames={scene.duration - 60}>
                <SingerOverlay />
              </Sequence>
            )}
            
            {index < scenes.length - 1 && (
              <TransitionSeries.Transition
                presentation={index === 2 ? slide({ direction: 'left' }) : fade()}
                timing={{ durationInFrames: 30 }}
              />
            )}
          </TransitionSeries.Sequence>
        ))}
      </TransitionSeries>
      
      {/* Audio track - replace with your MP3 */}
      {/* <Audio src="/your-track.mp3" /> */}
      
      {/* Film grain overlay */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          opacity: 0.03,
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E")`,
          pointerEvents: 'none',
          mixBlendMode: 'overlay',
        }}
      />
    </AbsoluteFill>
  );
};
