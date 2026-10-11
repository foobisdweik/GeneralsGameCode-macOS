// TheSuperHackers @port macOS: adapters for the AVAudioEngine audio device.
//
// The device comes from OKJID's macOS port (okji/feat/macos-port, commit
// a35dbbd). That port has its own path and logging helpers. This header maps
// them onto what this tree already provides, so the device sources stay close
// to the original:
//   NativeFileSystem::get_safe_path/exists/file_size -> apple_path::normalize + stat
//   DEBUG_AUDIO_MAC                                  -> DEBUG_LOG

#pragma once

#include "Common/Debug.h"

#include <cerrno>
#include <cstdint>
#include <cstdio>
#include <string>
#include <sys/stat.h>

namespace NativeFileSystem
{
	// Backslash separators to '/', with case-insensitive component lookup
	// (see osdep_compat/apple_path_shim.h). normalize() returns a thread-local
	// buffer, so copy it at once.
	inline std::string get_safe_path(const std::string& path)
	{
		const char* p = ::apple_path::normalize(path.c_str());
		return p ? std::string(p) : path;
	}

	inline bool exists(const std::string& path)
	{
		struct stat st;
		return ::stat(path.c_str(), &st) == 0;
	}

	inline std::uintmax_t file_size(const std::string& path)
	{
		struct stat st;
		return ::stat(path.c_str(), &st) == 0 ? (std::uintmax_t)st.st_size : 0;
	}

	// mkdir -p for the directory part of a file path.
	inline bool create_parent_directories(const std::string& filePath)
	{
		const std::string::size_type slash = filePath.find_last_of('/');
		if (slash == std::string::npos || slash == 0)
			return true;
		std::string dir;
		for (std::string::size_type i = 0; i <= slash; ++i) {
			if ((filePath[i] == '/' && i > 0) || i == slash) {
				dir = filePath.substr(0, i);
				if (::mkdir(dir.c_str(), 0755) != 0 && errno != EEXIST)
					return false;
			}
		}
		return true;
	}
}

#define DEBUG_AUDIO_MAC(m) DEBUG_LOG(m)
