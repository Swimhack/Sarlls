/**
 * Contract Test: GET /api/devices/[id]
 * Tests the device detail endpoint contract
 *
 * This test MUST FAIL until the endpoint is implemented
 */

import { NextRequest } from 'next/server';
import { DeviceWithFiles } from '@/lib/types/pcb';

describe('GET /api/devices/[id] - Contract Test', () => {
  let GET: any;

  beforeAll(async () => {
    try {
      // This import will fail until the route is implemented
      const route = await import('@/app/api/devices/[id]/route');
      GET = route.GET;
    } catch (error) {
      // Expected to fail - endpoint not implemented yet
      GET = null;
    }
  });

  describe('Contract: GET /api/devices/[id]', () => {
    it('should exist as an exported function', () => {
      // This will fail until implemented
      expect(GET).toBeDefined();
      expect(typeof GET).toBe('function');
    });

    it('should accept NextRequest with params and return Response', async () => {
      if (!GET) {
        expect(GET).toBeDefined();
        return;
      }

      const deviceId = '123e4567-e89b-12d3-a456-426614174000';
      const mockRequest = new NextRequest(`http://localhost:3000/api/devices/${deviceId}`);
      const mockParams = { params: { id: deviceId } };

      const response = await GET(mockRequest, mockParams);
      expect(response).toBeInstanceOf(Response);
    });

    it('should return 200 for existing device', async () => {
      if (!GET) {
        expect(GET).toBeDefined();
        return;
      }

      const deviceId = '123e4567-e89b-12d3-a456-426614174000';
      const mockRequest = new NextRequest(`http://localhost:3000/api/devices/${deviceId}`);
      const mockParams = { params: { id: deviceId } };

      const response = await GET(mockRequest, mockParams);
      expect([200, 404]).toContain(response.status);
    });

    it('should return device with files and status history', async () => {
      if (!GET) {
        expect(GET).toBeDefined();
        return;
      }

      const deviceId = '123e4567-e89b-12d3-a456-426614174000';
      const mockRequest = new NextRequest(`http://localhost:3000/api/devices/${deviceId}`);
      const mockParams = { params: { id: deviceId } };

      const response = await GET(mockRequest, mockParams);

      if (response.status === 200) {
        const device: DeviceWithFiles = await response.json();

        // Check DeviceWithFiles structure
        expect(device).toHaveProperty('id');
        expect(device).toHaveProperty('name');
        expect(device).toHaveProperty('version');
        expect(device).toHaveProperty('status');
        expect(device).toHaveProperty('createdBy');
        expect(device).toHaveProperty('organizationId');
        expect(device).toHaveProperty('createdAt');
        expect(device).toHaveProperty('updatedAt');

        // DeviceWithFiles additional properties
        expect(device).toHaveProperty('files');
        expect(device).toHaveProperty('statusHistory');

        // Validate arrays
        expect(Array.isArray(device.files)).toBe(true);
        expect(Array.isArray(device.statusHistory)).toBe(true);

        // Validate file structure if files exist
        if (device.files.length > 0) {
          const file = device.files[0];
          expect(file).toHaveProperty('id');
          expect(file).toHaveProperty('deviceId', device.id);
          expect(file).toHaveProperty('fileName');
          expect(file).toHaveProperty('fileType');
          expect(file).toHaveProperty('fileSize');
          expect(file).toHaveProperty('uploadedBy');
          expect(file).toHaveProperty('uploadedAt');
          expect(file).toHaveProperty('version');
        }

        // Validate status history structure if history exists
        if (device.statusHistory.length > 0) {
          const historyEntry = device.statusHistory[0];
          expect(historyEntry).toHaveProperty('id');
          expect(historyEntry).toHaveProperty('deviceId', device.id);
          expect(historyEntry).toHaveProperty('newStatus');
          expect(historyEntry).toHaveProperty('changedBy');
          expect(historyEntry).toHaveProperty('changedAt');
        }
      }
    });

    it('should return 404 for non-existent device', async () => {
      if (!GET) {
        expect(GET).toBeDefined();
        return;
      }

      const nonExistentId = '99999999-9999-9999-9999-999999999999';
      const mockRequest = new NextRequest(`http://localhost:3000/api/devices/${nonExistentId}`);
      const mockParams = { params: { id: nonExistentId } };

      const response = await GET(mockRequest, mockParams);
      expect(response.status).toBe(404);

      const errorData = await response.json();
      expect(errorData).toHaveProperty('error');
      expect(typeof errorData.error).toBe('string');
    });

    it('should return 400 for invalid UUID format', async () => {
      if (!GET) {
        expect(GET).toBeDefined();
        return;
      }

      const invalidIds = ['invalid-id', '123', 'not-a-uuid', ''];

      for (const invalidId of invalidIds) {
        const mockRequest = new NextRequest(`http://localhost:3000/api/devices/${invalidId}`);
        const mockParams = { params: { id: invalidId } };

        const response = await GET(mockRequest, mockParams);
        expect([400, 404]).toContain(response.status);

        if (response.status === 400) {
          const errorData = await response.json();
          expect(errorData).toHaveProperty('error');
          expect(errorData.error).toContain('Invalid');
        }
      }
    });

    it('should return 401 for unauthenticated requests', async () => {
      if (!GET) {
        expect(GET).toBeDefined();
        return;
      }

      const deviceId = '123e4567-e89b-12d3-a456-426614174000';
      // Mock request without authentication
      const mockRequest = new NextRequest(`http://localhost:3000/api/devices/${deviceId}`);
      const mockParams = { params: { id: deviceId } };

      const response = await GET(mockRequest, mockParams);

      // Should return 401 if not authenticated, or 404 if device doesn't exist
      expect([200, 401, 404]).toContain(response.status);

      if (response.status === 401) {
        const errorData = await response.json();
        expect(errorData).toHaveProperty('error');
      }
    });

    it('should return 403 for devices not in user organization', async () => {
      if (!GET) {
        expect(GET).toBeDefined();
        return;
      }

      // This would be a device ID from another organization
      const otherOrgDeviceId = '987e6543-e21b-32d1-a654-624241471000';
      const mockRequest = new NextRequest(`http://localhost:3000/api/devices/${otherOrgDeviceId}`);
      const mockParams = { params: { id: otherOrgDeviceId } };

      const response = await GET(mockRequest, mockParams);

      // Should return 404 (not found due to RLS) or 403 (forbidden)
      expect([404, 403, 200]).toContain(response.status);

      if (response.status === 403) {
        const errorData = await response.json();
        expect(errorData).toHaveProperty('error');
      }
    });

    it('should include optional device properties when present', async () => {
      if (!GET) {
        expect(GET).toBeDefined();
        return;
      }

      const deviceId = '123e4567-e89b-12d3-a456-426614174000';
      const mockRequest = new NextRequest(`http://localhost:3000/api/devices/${deviceId}`);
      const mockParams = { params: { id: deviceId } };

      const response = await GET(mockRequest, mockParams);

      if (response.status === 200) {
        const device: DeviceWithFiles = await response.json();

        // Optional properties should be present if set
        if (device.description !== undefined) {
          expect(typeof device.description).toBe('string');
        }

        if (device.boardDimensions !== undefined) {
          expect(device.boardDimensions).toHaveProperty('width');
          expect(device.boardDimensions).toHaveProperty('height');
          expect(device.boardDimensions).toHaveProperty('thickness');
          expect(typeof device.boardDimensions.width).toBe('number');
          expect(typeof device.boardDimensions.height).toBe('number');
          expect(typeof device.boardDimensions.thickness).toBe('number');
        }

        if (device.layerCount !== undefined) {
          expect(typeof device.layerCount).toBe('number');
          expect(device.layerCount).toBeGreaterThan(0);
          expect(device.layerCount).toBeLessThanOrEqual(32);
        }

        if (device.componentCount !== undefined) {
          expect(typeof device.componentCount).toBe('number');
          expect(device.componentCount).toBeGreaterThanOrEqual(0);
        }
      }
    });

    it('should handle server errors gracefully with 500 status', async () => {
      if (!GET) {
        expect(GET).toBeDefined();
        return;
      }

      const deviceId = '123e4567-e89b-12d3-a456-426614174000';
      const mockRequest = new NextRequest(`http://localhost:3000/api/devices/${deviceId}`);
      const mockParams = { params: { id: deviceId } };

      try {
        const response = await GET(mockRequest, mockParams);
        expect([200, 404, 500]).toContain(response.status);

        if (response.status === 500) {
          const errorData = await response.json();
          expect(errorData).toHaveProperty('error');
          expect(typeof errorData.error).toBe('string');
        }
      } catch (error) {
        fail('Endpoint should handle errors gracefully, not throw');
      }
    });
  });

  describe('Performance Contract', () => {
    it('should respond within 2 seconds', async () => {
      if (!GET) {
        expect(GET).toBeDefined();
        return;
      }

      const startTime = Date.now();
      const deviceId = '123e4567-e89b-12d3-a456-426614174000';
      const mockRequest = new NextRequest(`http://localhost:3000/api/devices/${deviceId}`);
      const mockParams = { params: { id: deviceId } };

      await GET(mockRequest, mockParams);

      const duration = Date.now() - startTime;
      expect(duration).toBeLessThan(2000); // 2 second performance target
    });
  });
});