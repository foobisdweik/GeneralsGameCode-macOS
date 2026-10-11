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

// TileData.cpp
// Class to handle tile data.
// Author: John Ahlquist, April 2001

#include "W3DDevice/GameClient/TileData.h"
#include "W3DDevice/GameClient/WorldHeightMap.h"



//
// TileData - no destructor.
//

//
// TileData - create a new texture tile .
//
TileData::TileData()
{

}

// Mip k (0-based) is TILE_PIXEL_EXTENT>>(k+1) pixels square.
UnsignedByte *TileData::mipPtr(Int k)
{
	Int offset = 0;
	for (Int i = 0; i < k; i++) {
		Int w = TILE_PIXEL_EXTENT >> (i+1);
		offset += w*w*TILE_BYTES_PER_PIXEL;
	}
	return m_tileDataMips + offset;
}

Bool TileData::hasRGBDataForWidth(Int width)
{
	if (width == TILE_PIXEL_EXTENT) return(true);
	for (Int k = 0; k < TILE_NUM_MIPS; k++) {
		if (width == (TILE_PIXEL_EXTENT >> (k+1))) return(true);
	}
	return(false);
}

UnsignedByte * TileData::getRGBDataForWidth(Int width)
{
	for (Int k = 0; k < TILE_NUM_MIPS; k++) {
		if (width == (TILE_PIXEL_EXTENT >> (k+1))) return(mipPtr(k));
	}
	// default
	return(m_tileData);
}

void TileData::updateMips()
{
	doMip(m_tileData, TILE_PIXEL_EXTENT, mipPtr(0));
	for (Int k = 1; k < TILE_NUM_MIPS; k++) {
		doMip(mipPtr(k-1), TILE_PIXEL_EXTENT >> k, mipPtr(k));
	}
}


void TileData::doMip(UnsignedByte *pHiRes, Int hiRow, UnsignedByte *pLoRes)
{
	Int i, j;
	for (i=0; i<hiRow; i+=2) {
		for (j=0; j<hiRow; j+=2) {
			Int pxl;
			Int ndx = (j*hiRow+i)*TILE_BYTES_PER_PIXEL;
			Int loNdx = (j/2)*(hiRow/2) + (i/2);
			loNdx *= TILE_BYTES_PER_PIXEL;
			Int p;
			for (p=0; p<TILE_BYTES_PER_PIXEL; p++,ndx++,loNdx++) {
				pxl = pHiRes[ndx] + pHiRes[ndx+TILE_BYTES_PER_PIXEL] + pHiRes[ndx+TILE_BYTES_PER_PIXEL*hiRow] + pHiRes[ndx+TILE_BYTES_PER_PIXEL*hiRow+TILE_BYTES_PER_PIXEL] +2;
				pxl /= 4;
				pLoRes[loNdx] = pxl;
			}
		}
	}

}

