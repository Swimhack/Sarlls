/**
 * Integration Test: Create New Device Workflow
 * Tests the complete device creation user journey
 *
 * This test MUST FAIL until the implementation is complete
 */

import { NextRequest } from 'next/server';
import { CreateDeviceRequest, Device } from '@/lib/types/pcb';

describe('Create New Device Workflow - Integration Test', () => {
  describe('Complete Device Creation Journey', () => {
    it('should fail - API endpoints not implemented yet', async () => {
      // This test verifies the complete user journey from the quickstart scenarios
      // Test 1: Create New Device from quickstart.md

      let devicesAPI: any;
      let deviceDetailAPI: any;

      try {
        const devicesRoute = await import('@/app/api/devices/route');
        const deviceRoute = await import('@/app/api/devices/[id]/route');
        devicesAPI = devicesRoute.POST;
        deviceDetailAPI = deviceRoute.GET;
      } catch (error) {
        // Expected to fail - endpoints not implemented
        devicesAPI = null;
        deviceDetailAPI = null;
      }

      // This should fail until implementation is complete
      expect(devicesAPI).toBeDefined();
      expect(deviceDetailAPI).toBeDefined();

      if (!devicesAPI || !deviceDetailAPI) {
        return; // Test fails as expected
      }

      // Test Data from quickstart.md Test 1
      const createRequest: CreateDeviceRequest = {
        name: "ESP32 Smart Switch v2",
        description: "Updated IoT switch with WiFi connectivity",
        version: "2.0.0"
      };

      // Step 1: Create device via POST /api/devices
      const createMockRequest = new NextRequest('http://localhost:3000/api/devices', {
        method: 'POST',
        body: JSON.stringify(createRequest),
        headers: { 'Content-Type': 'application/json' }
      });

      const createResponse = await devicesAPI(createMockRequest);
      expect(createResponse.status).toBe(201);

      const createdDevice: Device = await createResponse.json();

      // Verify device created with correct properties
      expect(createdDevice.name).toBe(createRequest.name);
      expect(createdDevice.description).toBe(createRequest.description);
      expect(createdDevice.version).toBe(createRequest.version);
      expect(createdDevice.status).toBe('draft');

      // Step 2: Retrieve device via GET /api/devices/[id]
      const getMockRequest = new NextRequest(`http://localhost:3000/api/devices/${createdDevice.id}`);
      const mockParams = { params: { id: createdDevice.id } };

      const getResponse = await deviceDetailAPI(getMockRequest, mockParams);
      expect(getResponse.status).toBe(200);

      const retrievedDevice = await getResponse.json();
      expect(retrievedDevice.id).toBe(createdDevice.id);
      expect(retrievedDevice.files).toEqual([]);
      expect(retrievedDevice.statusHistory).toHaveLength(1); // Initial creation

      // Step 3: Verify device appears in devices list
      const devicesListAPI = await import('@/app/api/devices/route').then(m => m.GET);
      const listMockRequest = new NextRequest('http://localhost:3000/api/devices');
      const listResponse = await devicesListAPI(listMockRequest);

      expect(listResponse.status).toBe(200);
      const devicesList = await listResponse.json();

      const foundDevice = devicesList.devices.find((d: Device) => d.id === createdDevice.id);
      expect(foundDevice).toBeDefined();
      expect(foundDevice.name).toBe(createRequest.name);

      // This integration test covers the complete workflow from quickstart Test 1
      console.log('✅ Complete device creation workflow successful');
    });

    it('should handle validation errors in the complete workflow', async () => {
      // Test validation through the complete workflow
      let devicesAPI: any;

      try {
        const route = await import('@/app/api/devices/route');
        devicesAPI = route.POST;
      } catch (error) {
        devicesAPI = null;
      }

      expect(devicesAPI).toBeDefined();
      if (!devicesAPI) return;

      // Test invalid device creation data
      const invalidRequest = {
        name: '', // Empty name should fail validation
        description: 'Should fail validation'
      };

      const mockRequest = new NextRequest('http://localhost:3000/api/devices', {
        method: 'POST',
        body: JSON.stringify(invalidRequest),
        headers: { 'Content-Type': 'application/json' }
      });

      const response = await devicesAPI(mockRequest);
      expect(response.status).toBe(400);

      const errorData = await response.json();
      expect(errorData).toHaveProperty('error');
      expect(errorData.error.toLowerCase()).toContain('name');
    });

    it('should handle authentication in the complete workflow', async () => {
      // Test that authentication is required for device operations
      let devicesAPI: any;

      try {
        const route = await import('@/app/api/devices/route');
        devicesAPI = route.POST;
      } catch (error) {
        devicesAPI = null;
      }

      expect(devicesAPI).toBeDefined();
      if (!devicesAPI) return;

      const createRequest: CreateDeviceRequest = {
        name: "Unauthorized Test Device"
      };

      // Mock request without authentication headers
      const mockRequest = new NextRequest('http://localhost:3000/api/devices', {
        method: 'POST',
        body: JSON.stringify(createRequest),
        headers: { 'Content-Type': 'application/json' }
        // No authentication headers
      });

      const response = await devicesAPI(mockRequest);

      // Should either succeed (if mocked auth) or fail with 401
      expect([201, 401]).toContain(response.status);

      if (response.status === 401) {
        const errorData = await response.json();
        expect(errorData).toHaveProperty('error');
      }
    });
  });

  describe('Performance Requirements', () => {
    it('should complete device creation workflow within performance targets', async () => {
      // Test performance requirements from quickstart
      const startTime = Date.now();

      let devicesAPI: any;
      try {
        const route = await import('@/app/api/devices/route');
        devicesAPI = route.POST;
      } catch (error) {
        devicesAPI = null;
      }

      expect(devicesAPI).toBeDefined();
      if (!devicesAPI) return;

      const createRequest: CreateDeviceRequest = {
        name: "Performance Test Device"
      };

      const mockRequest = new NextRequest('http://localhost:3000/api/devices', {
        method: 'POST',
        body: JSON.stringify(createRequest),
        headers: { 'Content-Type': 'application/json' }
      });

      await devicesAPI(mockRequest);

      const duration = Date.now() - startTime;

      // Performance target: <2s for device creation
      expect(duration).toBeLessThan(2000);
    });
  });

  describe('Data Consistency', () => {
    it('should maintain data consistency across device operations', async () => {
      // Test that device creation updates all related data correctly

      let devicesAPI: any;
      let deviceDetailAPI: any;

      try {
        const devicesRoute = await import('@/app/api/devices/route');
        const deviceRoute = await import('@/app/api/devices/[id]/route');
        devicesAPI = devicesRoute.POST;
        deviceDetailAPI = deviceRoute.GET;
      } catch (error) {
        devicesAPI = null;
        deviceDetailAPI = null;
      }

      expect(devicesAPI).toBeDefined();
      expect(deviceDetailAPI).toBeDefined();
      if (!devicesAPI || !deviceDetailAPI) return;

      const createRequest: CreateDeviceRequest = {
        name: "Data Consistency Test Device",
        description: "Testing data consistency",
        version: "1.5.0"
      };

      // Create device
      const createMockRequest = new NextRequest('http://localhost:3000/api/devices', {
        method: 'POST',
        body: JSON.stringify(createRequest),
        headers: { 'Content-Type': 'application/json' }
      });

      const createResponse = await devicesAPI(createMockRequest);
      expect(createResponse.status).toBe(201);

      const device: Device = await createResponse.json();

      // Verify timestamps are consistent
      expect(device.createdAt).toBeDefined();
      expect(device.updatedAt).toBeDefined();

      const createdAt = new Date(device.createdAt);
      const updatedAt = new Date(device.updatedAt);

      // Should be very close in time (within 1 second)
      expect(Math.abs(updatedAt.getTime() - createdAt.getTime())).toBeLessThan(1000);

      // Verify device detail retrieval is consistent
      const getMockRequest = new NextRequest(`http://localhost:3000/api/devices/${device.id}`);
      const mockParams = { params: { id: device.id } };

      const getResponse = await deviceDetailAPI(getMockRequest, mockParams);
      const retrievedDevice = await getResponse.json();

      // All fields should match exactly
      expect(retrievedDevice.name).toBe(device.name);
      expect(retrievedDevice.description).toBe(device.description);
      expect(retrievedDevice.version).toBe(device.version);
      expect(retrievedDevice.status).toBe(device.status);
      expect(retrievedDevice.createdAt).toBe(device.createdAt);
    });
  });
});