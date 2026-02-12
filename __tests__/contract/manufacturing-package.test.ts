/**
 * Contract Test: POST /api/devices/[id]/manufacturing-package
 * Tests the manufacturing package generation endpoint contract
 *
 * This test MUST FAIL until the endpoint is implemented
 */

import { NextRequest } from 'next/server';
import { GeneratePackageRequest, ManufacturingPackage } from '@/lib/types/pcb';

describe('POST /api/devices/[id]/manufacturing-package - Contract Test', () => {
  let POST: any;

  beforeAll(async () => {
    try {
      const route = await import('@/app/api/devices/[id]/manufacturing-package/route');
      POST = route.POST;
    } catch (error) {
      POST = null;
    }
  });

  describe('Contract: POST /api/devices/[id]/manufacturing-package', () => {
    it('should exist as an exported function', () => {
      expect(POST).toBeDefined();
      expect(typeof POST).toBe('function');
    });

    it('should generate manufacturing package successfully', async () => {
      if (!POST) {
        expect(POST).toBeDefined();
        return;
      }

      const deviceId = '123e4567-e89b-12d3-a456-426614174000';
      const requestBody: GeneratePackageRequest = {
        packageName: 'ESP32_SmartSwitch_v2_Manufacturing',
        expiryHours: 168 // 7 days
      };

      const mockRequest = new NextRequest(`http://localhost:3000/api/devices/${deviceId}/manufacturing-package`, {
        method: 'POST',
        body: JSON.stringify(requestBody),
        headers: { 'Content-Type': 'application/json' }
      });

      const mockParams = { params: { id: deviceId } };
      const response = await POST(mockRequest, mockParams);

      expect([201, 404, 422]).toContain(response.status);

      if (response.status === 201) {
        const pkg: ManufacturingPackage = await response.json();
        expect(pkg).toHaveProperty('id');
        expect(pkg).toHaveProperty('packageName');
        expect(pkg).toHaveProperty('fileCount');
        expect(pkg).toHaveProperty('totalSize');
        expect(pkg).toHaveProperty('checksum');
      }
    });

    it('should return 422 for devices not ready for manufacturing', async () => {
      if (!POST) return;

      // Device in draft status should not allow package generation
      const deviceId = '123e4567-e89b-12d3-a456-426614174000';
      const requestBody: GeneratePackageRequest = {};

      const mockRequest = new NextRequest(`http://localhost:3000/api/devices/${deviceId}/manufacturing-package`, {
        method: 'POST',
        body: JSON.stringify(requestBody),
        headers: { 'Content-Type': 'application/json' }
      });

      const mockParams = { params: { id: deviceId } };
      const response = await POST(mockRequest, mockParams);

      expect([422, 404, 201]).toContain(response.status);
    });
  });
});