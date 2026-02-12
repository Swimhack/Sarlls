/**
 * Contract Test: GET /api/devices/[id]/history
 * Tests the device status history endpoint contract
 *
 * This test MUST FAIL until the endpoint is implemented
 */

import { NextRequest } from 'next/server';
import { StatusHistory } from '@/lib/types/pcb';

describe('GET /api/devices/[id]/history - Contract Test', () => {
  let GET: any;

  beforeAll(async () => {
    try {
      const route = await import('@/app/api/devices/[id]/history/route');
      GET = route.GET;
    } catch (error) {
      GET = null;
    }
  });

  describe('Contract: GET /api/devices/[id]/history', () => {
    it('should exist as an exported function', () => {
      expect(GET).toBeDefined();
      expect(typeof GET).toBe('function');
    });

    it('should return status history with correct structure', async () => {
      if (!GET) {
        expect(GET).toBeDefined();
        return;
      }

      const deviceId = '123e4567-e89b-12d3-a456-426614174000';
      const mockRequest = new NextRequest(`http://localhost:3000/api/devices/${deviceId}/history`);
      const mockParams = { params: { id: deviceId } };

      const response = await GET(mockRequest, mockParams);
      expect([200, 404]).toContain(response.status);

      if (response.status === 200) {
        const data = await response.json();
        expect(data).toHaveProperty('history');
        expect(Array.isArray(data.history)).toBe(true);

        if (data.history.length > 0) {
          const entry: StatusHistory = data.history[0];
          expect(entry).toHaveProperty('id');
          expect(entry).toHaveProperty('deviceId');
          expect(entry).toHaveProperty('newStatus');
          expect(entry).toHaveProperty('changedBy');
          expect(entry).toHaveProperty('changedAt');
        }
      }
    });

    it('should return 404 for non-existent device', async () => {
      if (!GET) return;

      const nonExistentId = '99999999-9999-9999-9999-999999999999';
      const mockRequest = new NextRequest(`http://localhost:3000/api/devices/${nonExistentId}/history`);
      const mockParams = { params: { id: nonExistentId } };

      const response = await GET(mockRequest, mockParams);
      expect(response.status).toBe(404);
    });
  });
});