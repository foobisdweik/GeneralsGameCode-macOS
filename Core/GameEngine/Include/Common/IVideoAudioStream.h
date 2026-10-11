#pragma once

#include <stdint.h>

class IVideoAudioStream
{
public:
    virtual ~IVideoAudioStream() {}

    virtual void reset() = 0;
    virtual void play() = 0;
    virtual void update() = 0;
    virtual void bufferData(uint8_t* data, int size, int channels, int bitsPerSample, int sampleRate) = 0;
};

// TheSuperHackers @port macOS: the active video-audio stream, or nullptr when
// the active audio manager has none (for example GEN_AUDIO=miles). Use this
// instead of casting AudioManager::getHandleForBink(), whose type depends on
// the audio manager.
IVideoAudioStream* GetVideoAudioStream();
