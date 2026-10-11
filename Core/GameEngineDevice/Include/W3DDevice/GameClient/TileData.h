/*
**	Command & Conquer Generals Zero Hour(tm)
**	Copyright 2025 Electronic Arts Inc.
**
**	This program is free software: you can redistribute it and/or modify
**	it under the terms of the GNU General Public License as published by
**	the Free Software Foundation, either version 3 of the License, or
**	(at your option) any later version.
**
**	This program is distributed in the hope that it will be useful,
**	but WITHOUT ANY WARRANTY; without even the implied warranty of
**	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
**	GNU General Public License for more details.
**
**	You should have received a copy of the GNU General Public License
**	along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

////////////////////////////////////////////////////////////////////////////////
//																																						//
//  (c) 2001-2003 Electronic Arts Inc.																				//
//																																						//
////////////////////////////////////////////////////////////////////////////////

// TileData.h
// Class to hold 1 tile's data.
// Author: John Ahlquist, April 2001

#pragma once

#include "Lib/BaseType.h"
#include "WWLib/refcount.h"
#include "Common/AsciiString.h"

typedef struct {
	Int blendNdx;
	UnsignedByte horiz;
	UnsignedByte vert;
	UnsignedByte rightDiagonal;
	UnsignedByte leftDiagonal;
	UnsignedByte inverted;
	UnsignedByte longDiagonal;
	Int customBlendEdgeClass; // Class of texture for a blend edge.  -1 means use alpha.
} TBlendTileInfo;

#define INVERTED_MASK	0x1		//AND this with TBlendTileInfo.inverted to get actual inverted state
#define FLIPPED_MASK	0x2		//AND this with TBlendTileInfo.inverted to get forced flip state (for horizontal/vertical flips).
// TheSuperHackers @port macOS: terrain and tree tiles are stored at
// TILE_SCALE times the original 64 px, so 2x-upscaled terrain art keeps its
// detail. Source images stay laid out in 64 px tiles (TILE_NATIVE_EXTENT);
// WorldHeightMap::readTiles upsamples them unless the TGA image ID carries
// TILE_HIRES_TGA_ID, which marks art that is already at TILE_PIXEL_EXTENT.
// The atlas layout (tiles per row) is unchanged; only its pixel size scales.
#define TILE_SCALE 2
#define TILE_NATIVE_EXTENT 64
#define TILE_HIRES_TGA_ID "GZH_TILE128"
#define TILE_PIXEL_EXTENT (TILE_NATIVE_EXTENT*TILE_SCALE)
#define TILE_BYTES_PER_PIXEL 4
#define DATA_LEN_BYTES TILE_PIXEL_EXTENT*TILE_PIXEL_EXTENT*TILE_BYTES_PER_PIXEL
#define DATA_LEN_PIXELS TILE_PIXEL_EXTENT*TILE_PIXEL_EXTENT
#define TILE_NUM_MIPS 7 // levels below TILE_PIXEL_EXTENT, down to 1x1
#define TEXTURE_WIDTH (2048*TILE_SCALE) // was 1024 jba

/** This class holds the bitmap data from the .tga texture files.  It is used to
create the D3D texture in the game and 3d windows, and to create DIB data for the
2d window. */
class TileData : public RefCountClass
{
protected:

	// data is bgrabgrabgra to be compatible with windows blt. jba.
	// Also, first byte is lower left pixel, not upper left pixel.
	// so 0,0 is lower left, not upper left.
	UnsignedByte m_tileData[DATA_LEN_BYTES];
	/// Mipped down copies of the tile data, (TILE_PIXEL_EXTENT>>(k+1))^2 pixels
	/// each, packed back to back. Total is less than a third of DATA_LEN_BYTES.
	UnsignedByte m_tileDataMips[DATA_LEN_BYTES/3];
	UnsignedByte *mipPtr(Int k);

public:
	ICoord2D	m_tileLocationInTexture;


protected:
	/** doMip - generates the next mip level mipping pHiRes down to pLoRes.
				pLoRes is 1/2 the width of pHiRes, and both are square. */
	static void doMip(UnsignedByte *pHiRes, Int hiRow, UnsignedByte *pLoRes);



public:
	TileData();

public:
	UnsignedByte *getDataPtr() {return(m_tileData);};
	static Int dataLen() {return(DATA_LEN_BYTES);};

	void updateMips();

	Bool hasRGBDataForWidth(Int width);
	UnsignedByte *getRGBDataForWidth(Int width);
};
