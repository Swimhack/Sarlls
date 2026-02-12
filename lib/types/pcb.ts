/**
 * PCB Manufacturing TypeScript Types
 * Created: 2025-09-23
 * Feature: PCB Manufacturing Readiness
 */

// Base types for database enums
export type DeviceStatus =
  | 'draft'
  | 'review'
  | 'ready_for_manufacturing'
  | 'submitted'
  | 'in_production'
  | 'completed'
  | 'cancelled';

export type FileType =
  | 'gerber_zip'
  | 'bom_csv'
  | 'cpl_csv'
  | 'schematic_pdf'
  | 'technical_spec'
  | 'assembly_drawing'
  | 'test_procedure'
  | 'other';

// Board dimensions interface
export interface BoardDimensions {
  width: number;  // mm
  height: number; // mm
  thickness: number; // mm
}

// File metadata interfaces
export interface GerberMetadata {
  layerCount: number;
  boardOutline: boolean;
  drillFiles: number;
  fabricationNotes?: string;
}

export interface BomMetadata {
  componentCount: number;
  uniqueParts: number;
  estimatedCost?: number; // USD
  missingParts: string[];
}

export interface CplMetadata {
  placementCount: number;
  topSideComponents: number;
  bottomSideComponents: number;
  rotationFormat: string; // 'degrees' or 'radians'
}

export interface FileMetadata {
  gerber?: GerberMetadata;
  bom?: BomMetadata;
  cpl?: CplMetadata;
}

// Core entity interfaces
export interface Device {
  id: string;
  name: string;
  description?: string;
  version: string;
  status: DeviceStatus;
  boardDimensions?: BoardDimensions;
  layerCount?: number;
  componentCount?: number;
  createdBy: string;
  organizationId: string;
  createdAt: string;
  updatedAt: string;
}

export interface DeviceFile {
  id: string;
  deviceId: string;
  fileName: string;
  fileType: FileType;
  fileSize: number;
  filePath: string;
  contentHash: string;
  metadata?: FileMetadata;
  uploadedBy: string;
  uploadedAt: string;
  version: number;
}

export interface StatusHistory {
  id: string;
  deviceId: string;
  previousStatus?: DeviceStatus;
  newStatus: DeviceStatus;
  changedBy: string;
  changedAt: string;
  notes?: string;
  metadata?: Record<string, any>;
}

export interface ManufacturingPackage {
  id: string;
  deviceId: string;
  packageName: string;
  packagePath: string;
  fileCount: number;
  totalSize: number;
  checksum: string;
  generatedBy: string;
  generatedAt: string;
  expiryDate?: string;
}

export interface Manufacturer {
  id: string;
  name: string;
  contactEmail: string;
  contactPhone?: string;
  website?: string;
  capabilities: string[];
  leadTimeDays: number;
  qualityRating?: number; // 1-5 stars
  notes?: string;
  addedBy: string;
  organizationId: string;
  createdAt: string;
  updatedAt: string;
}

// Extended interfaces for API responses
export interface DeviceWithFiles extends Device {
  files: DeviceFile[];
  statusHistory: StatusHistory[];
}

export interface DeviceWithStats extends Device {
  fileCount: number;
  totalFileSize: number;
  lastUploadedAt?: string;
  manufacturingPackageCount: number;
}

// Request/Response types for API endpoints
export interface CreateDeviceRequest {
  name: string;
  description?: string;
  version?: string; // defaults to '1.0.0'
}

export interface UpdateDeviceRequest {
  name?: string;
  description?: string;
  version?: string;
}

export interface UpdateStatusRequest {
  status: DeviceStatus;
  notes?: string;
  metadata?: Record<string, any>;
}

export interface GeneratePackageRequest {
  packageName?: string;
  includeTypes?: FileType[];
  expiryHours?: number; // defaults to 168 (7 days)
}

export interface FileUploadRequest {
  file: File;
  fileType: FileType;
  description?: string;
}

// Pagination and filtering types
export interface PaginationParams {
  limit?: number;
  offset?: number;
}

export interface DeviceFilters {
  status?: DeviceStatus;
  createdBy?: string;
  search?: string; // searches name and description
}

export interface FileFilters {
  type?: FileType;
  uploadedBy?: string;
}

// API response wrappers
export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  limit: number;
  offset: number;
}

export interface DeviceListResponse extends PaginatedResponse<DeviceWithStats> {}

export interface FileListResponse {
  files: DeviceFile[];
}

export interface PackageListResponse {
  packages: ManufacturingPackage[];
}

export interface StatusHistoryResponse {
  history: StatusHistory[];
}

// Validation types
export interface ValidationError {
  field: string;
  message: string;
  code: string;
}

export interface DeviceValidation {
  isValid: boolean;
  errors: ValidationError[];
  warnings: string[];
  requiredFiles: FileType[];
  missingFiles: FileType[];
}

// Status transition validation
export interface StatusTransition {
  from: DeviceStatus;
  to: DeviceStatus;
  allowed: boolean;
  requirements: string[];
  warnings: string[];
}

// File processing types
export interface FileProcessingResult {
  success: boolean;
  metadata?: FileMetadata;
  errors: string[];
  warnings: string[];
}

export interface PackageGenerationResult {
  success: boolean;
  packageId?: string;
  downloadUrl?: string;
  errors: string[];
  fileCount: number;
  totalSize: number;
}

// WebSocket/real-time update types
export interface DeviceUpdate {
  type: 'status_change' | 'file_upload' | 'package_generated';
  deviceId: string;
  data: any;
  timestamp: string;
}

// Utility types
export type DeviceStatusFlow = {
  [K in DeviceStatus]: DeviceStatus[];
};

export type FileTypeDisplayNames = {
  [K in FileType]: string;
};

export type DeviceStatusDisplayNames = {
  [K in DeviceStatus]: string;
};

// Constants for validation
export const DEVICE_STATUS_FLOW: DeviceStatusFlow = {
  draft: ['review', 'cancelled'],
  review: ['draft', 'ready_for_manufacturing', 'cancelled'],
  ready_for_manufacturing: ['submitted', 'review', 'cancelled'],
  submitted: ['in_production', 'cancelled'],
  in_production: ['completed', 'cancelled'],
  completed: [],
  cancelled: []
};

export const FILE_TYPE_DISPLAY_NAMES: FileTypeDisplayNames = {
  gerber_zip: 'Gerber Files (ZIP)',
  bom_csv: 'Bill of Materials (CSV)',
  cpl_csv: 'Component Placement List (CSV)',
  schematic_pdf: 'Schematic (PDF)',
  technical_spec: 'Technical Specification',
  assembly_drawing: 'Assembly Drawing',
  test_procedure: 'Test Procedure',
  other: 'Other File'
};

export const DEVICE_STATUS_DISPLAY_NAMES: DeviceStatusDisplayNames = {
  draft: 'Draft',
  review: 'Under Review',
  ready_for_manufacturing: 'Ready for Manufacturing',
  submitted: 'Submitted to Manufacturer',
  in_production: 'In Production',
  completed: 'Completed',
  cancelled: 'Cancelled'
};

// Required files for status transitions
export const REQUIRED_FILES_FOR_REVIEW: FileType[] = [
  'gerber_zip',
  'bom_csv'
];

export const REQUIRED_FILES_FOR_MANUFACTURING: FileType[] = [
  'gerber_zip',
  'bom_csv',
  'cpl_csv'
];

// File size limits (in bytes)
export const MAX_FILE_SIZE = 200 * 1024 * 1024; // 200MB
export const MAX_PACKAGE_SIZE = 500 * 1024 * 1024; // 500MB

// Performance targets
export const PERFORMANCE_TARGETS = {
  FILE_UPLOAD_TIMEOUT: 30000, // 30 seconds
  PACKAGE_GENERATION_TIMEOUT: 15000, // 15 seconds
  METADATA_EXTRACTION_TIMEOUT: 10000, // 10 seconds
} as const;

// Error codes
export const ERROR_CODES = {
  DEVICE_NOT_FOUND: 'DEVICE_NOT_FOUND',
  INVALID_STATUS_TRANSITION: 'INVALID_STATUS_TRANSITION',
  FILE_TOO_LARGE: 'FILE_TOO_LARGE',
  INVALID_FILE_TYPE: 'INVALID_FILE_TYPE',
  MISSING_REQUIRED_FILES: 'MISSING_REQUIRED_FILES',
  PACKAGE_EXPIRED: 'PACKAGE_EXPIRED',
  INSUFFICIENT_PERMISSIONS: 'INSUFFICIENT_PERMISSIONS',
  VALIDATION_FAILED: 'VALIDATION_FAILED'
} as const;

export type ErrorCode = typeof ERROR_CODES[keyof typeof ERROR_CODES];