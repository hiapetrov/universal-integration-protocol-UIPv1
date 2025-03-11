/**
 * Universal Connector Block (UCB) Reference Implementation for TypeScript
 * 
 * This module provides a TypeScript implementation of the Universal Connector Block
 * as defined in the Universal Integration Protocol specification.
 */

// Type definitions
export type UssType = 
  | 'String' 
  | 'Integer' 
  | 'Float' 
  | 'Boolean'
  | 'Date'
  | 'DateTime'
  | 'Object'
  | 'Array'
  | 'Binary'
  | 'Null'
  | 'Any'
  | `Array<${string}>`
  | 'Union';

export enum AuthMethod {
  NONE = 'none',
  API_KEY = 'api_key',
  BEARER = 'bearer',
  BASIC = 'basic',
  OAUTH2 = 'oauth2',
  CUSTOM = 'custom'
}

export enum ParameterLocation {
  PATH = 'path',
  QUERY = 'query',
  HEADER = 'header',
  BODY = 'body'
}

export enum HttpMethod {
  GET = 'GET',
  POST = 'POST',
  PUT = 'PUT',
  DELETE = 'DELETE',
  PATCH = 'PATCH',
  OPTIONS = 'OPTIONS',
  HEAD = 'HEAD'
}

export interface Parameter {
  name: string;
  type: UssType;
  location: ParameterLocation;
  required: boolean;
  description?: string;
  defaultValue?: any;
}

export interface Response {
  statusCode: number;
  contentType: string;
  schema?: Record<string, any>;
  description?: string;
}

export interface Endpoint {
  path: string;
  method: HttpMethod;
  parameters: Parameter[];
  responses: Response[];
  authRequired: boolean;
  authMethods: AuthMethod[];
  rateLimit?: number;
  description?: string;
}

export interface ApiDescriptor {
  name: string;
  version: string;
  basePath: string;
  endpoints: Endpoint[];
  description?: string;
}

export interface UssDescriptor {
  '@context': string;
  '@type': string;
  '@id': string;
  version: string;
  name: string;
  basePath: string;
  endpoints: Record<string, any>[];
  description?: string;
}

export interface ErrorDetail {
  [key: string]: any;
}

export interface UcbErrorData {
  errorCode: string;
  message: string;
  details: ErrorDetail[];
  requestId: string;
  timestamp: string;
  statusCode: number;
}

export interface CacheEntry<T> {
  value: T;
  timestamp: number;
}

export interface RequestOptions {
  method?: string;
  headers?: Record<string, string>;
  body?: any;
  useCache?: boolean;
  retryAttempts?: number;
  timeout?: number;
}

export interface AuthOptions {
  type: string;
  token?: string;
  username?: string;
  password?: string;
  keyName?: string;
  keyValue?: string;
  keyLocation?: string;
}

/**
 * UCB Error class for standardized error handling
 */
export class UcbError extends Error {
  errorCode: string;
  details: ErrorDetail[];
  requestId: string;
  timestamp: string;
  statusCode: number;

  constructor(errorCode: string, message: string, details: ErrorDetail[] = [], statusCode = 400) {
    super(message);
    this.name = 'UcbError';
    this.errorCode = errorCode;
    this.message = message;
    this.details = details || [];
    this.statusCode = statusCode;
    this.requestId = crypto.randomUUID();
    this.timestamp = new Date().toISOString();
  }

  toJSON(): UcbErrorData {
    return {
      errorCode: this.errorCode,
      message: this.message,
      details: this.details,
      requestId: this.requestId,
      timestamp: this.timestamp,
      statusCode: this.statusCode
    };
  }
}

/**
 * Validation Error class for input validation failures
 */
export class ValidationError extends UcbError {
  constructor(message: string, details: ErrorDetail[] = []) {
    super('VALIDATION_ERROR', message, details, 400);
  }
}

/**
 * Type Mapper utility for converting between TypeScript and USS types
 */
export class TypeMapper {
  private static TS_TO_USS: Record<string, UssType> = {
    'string': 'String',
    'number': 'Float',
    'boolean': 'Boolean',
    'object': 'Object',
    'undefined': 'Null',
    'function': 'Any',
    'symbol': 'Any',
    'bigint': 'String'
  };

  private static USS_TO_TS: Record<string, string> = {
    'String': 'string',
    'Integer': 'number',
    'Float': 'number',
    'Boolean': 'boolean',
    'Object': 'object',
    'Array': 'Array',
    'DateTime': 'string',
    'Date': 'string',
    'Binary': 'Uint8Array',
    'Null': 'null',
    'Any': 'any'
  };

  static tsToUss(tsType: string): UssType {
    if (tsType in this.TS_TO_USS) {
      return this.TS_TO_USS[tsType] as UssType;
    }
    
    // Handle array types
    if (tsType.startsWith('Array<') || tsType.endsWith('[]')) {
      let itemType = '';
      if (tsType.startsWith('Array<')) {
        itemType = tsType.substring(6, tsType.length - 1);
      } else {
        itemType = tsType.substring(0, tsType.length - 2);
      }
      const ussItemType = this.tsToUss(itemType);
      return `Array<${ussItemType}>` as UssType;
    }
    
    return 'Any';
  }

  static inferTypeFromValue(value: any): UssType {
    if (value === null) {
      return 'Null';
    }
    
    const jsType = typeof value;
    if (jsType in this.TS_TO_USS) {
      // Special handling for integers vs floats
      if (jsType === 'number') {
        return Number.isInteger(value) ? 'Integer' : 'Float';
      }
      return this.TS_TO_USS[jsType];
    }
    
    // Check if it's an array
    if (Array.isArray(value)) {
      return 'Array';
    }
    
    // Check if it's a Date
    if (value instanceof Date) {
      return 'DateTime';
    }
    
    // Default to Any for unknown types
    return 'Any';
  }

  static validateAndConvert(value: any, ussType: UssType): any {
    if (ussType === 'Any') {
      return value;
    }
    
    if (ussType === 'Null' && value !== null) {
      throw new ValidationError('Expected null value', [
        { value, expectedType: 'Null' }
      ]);
    }
    
    if (value === null && !ussType.startsWith('Union')) {
      throw new ValidationError(`Unexpected null value for type ${ussType}`,
        [{ value: null, expectedType: ussType }]);
    }
    
    switch (ussType) {
      case 'String':
        if (typeof value !== 'string') {
          return String(value); // Attempt conversion
        }
        return value;
        
      case 'Integer':
        if (typeof value === 'number' && Number.isInteger(value)) {
          return value;
        }
        try {
          const num = parseInt(String(value), 10);
          if (isNaN(num)) {
            throw new Error('Not a number');
          }
          return num;
        } catch (e) {
          throw new ValidationError(`Cannot convert ${value} to Integer`,
            [{ value, expectedType: 'Integer' }]);
        }
        
      case 'Float':
        if (typeof value === 'number') {
          return value;
        }
        try {
          const num = parseFloat(String(value));
          if (isNaN(num)) {
            throw new Error('Not a number');
          }
          return num;
        } catch (e) {
          throw new ValidationError(`Cannot convert ${value} to Float`,
            [{ value, expectedType: 'Float' }]);
        }
        
      case 'Boolean':
        if (typeof value === 'boolean') {
          return value;
        }
        if (typeof value === 'string') {
          const lowerValue = value.toLowerCase();
          if (['true', 'yes', '1'].includes(lowerValue)) {
            return true;
          }
          if (['false', 'no', '0'].includes(lowerValue)) {
            return false;
          }
        }
        throw new ValidationError(`Cannot convert ${value} to Boolean`,
          [{ value, expectedType: 'Boolean' }]);
          
      case 'Object':
        if (typeof value !== 'object' || value === null || Array.isArray(value)) {
          throw new ValidationError(`Expected Object, got ${value === null ? 'null' : Array.isArray(value) ? 'Array' : typeof value}`,
            [{ value, expectedType: 'Object' }]);
        }
        return value;
        
      default:
        if (ussType.startsWith('Array<')) {
          if (!Array.isArray(value)) {
            throw new ValidationError(`Expected Array, got ${typeof value}`,
              [{ value, expectedType: 'Array' }]);
          }
          
          // If we have Array<Type>, validate each element
          if (ussType !== 'Array' && ussType.includes('<')) {
            const itemType = ussType.substring(6, ussType.length - 1) as UssType;
            return value.map(item => this.validateAndConvert(item, itemType));
          }
          return value;
        }
        
        return value;
    }
  }
}

/**
 * Circuit Breaker implementation for resilient API calls
 */
class CircuitBreaker {
  private failureThreshold: number;
  private resetTimeout: number;
  private failureCount: number;
  private lastFailureTime: number | null;
  private state: 'CLOSED' | 'OPEN' | 'HALF_OPEN';
  
  constructor(failureThreshold = 5, resetTimeout = 60000) {
    this.failureThreshold = failureThreshold;
    this.resetTimeout = resetTimeout;
    this.failureCount = 0;
    this.lastFailureTime = null;
    this.state = 'CLOSED';
  }
  
  recordSuccess(): void {
    this.failureCount = 0;
    this.state = 'CLOSED';
  }
  
  recordFailure(): void {
    this.failureCount++;
    this.lastFailureTime = Date.now();
    
    if (this.failureCount >= this.failureThreshold) {
      this.state = 'OPEN';
    }
  }
  
  allowRequest(): boolean {
    if (this.state === 'CLOSED') {
      return true;
    }
    
    if (this.state === 'OPEN') {
      // Check if reset timeout has elapsed
      if (this.lastFailureTime) {
        const elapsed = Date.now() - this.lastFailureTime;
        if (elapsed > this.resetTimeout) {
          this.state = 'HALF_OPEN';
          return true;
        }
      }
      return false;
    }
    
    if (this.state === 'HALF_OPEN') {
      return true;
    }
    
    return true;
  }
}

/**
 * Rate Limiter implementation for API call throttling
 */
class RateLimiter {
  private callsPerMinute: number;
  private callHistory: number[];
  
  constructor(callsPerMinute = 60) {
    this.callsPerMinute = callsPerMinute;
    this.callHistory = [];
  }
  
  allowRequest(): boolean {
    const now = Date.now();
    
    // Remove calls older than 1 minute
    this.callHistory = this.callHistory.filter(timestamp => 
      (now - timestamp) < 60000
    );
    
    // Check if we're under the limit
    if (this.callHistory.length < this.callsPerMinute) {
      this.callHistory.push(now);
      return true;
    }
    
    return false;
  }
}

/**
 * Cacher implementation for API response caching
 */
class Cacher {
  private cache: Map<string, CacheEntry<any>>;
  private ttlMs: number;
  
  constructor(ttlSeconds = 300) {
    this.cache = new Map();
    this.ttlMs = ttlSeconds * 1000;
  }
  
  get<T>(key: string): T | null {
    if (!this.cache.has(key)) {
      return null;
    }
    
    const entry = this.cache.get(key) as CacheEntry<T>;
    if ((Date.now() - entry.timestamp) > this.ttlMs) {
      // Entry expired
      this.cache.delete(key);
      return null;
    }
    
    return entry.value;
  }
  
  set<T>(key: string, value: T): void {
    this.cache.set(key, {
      value,
      timestamp: Date.now()
    });
  }
  
  generateKey(...args: any[]): string {
    // Convert all arguments to a string representation
    const keyStr = JSON.stringify(args);
    
    // Create a hash of the key string
    return this.hashString(keyStr);
  }
  
  private hashString(str: string): string {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32bit integer
    }
    return hash.toString(16);
  }
}

/**
 * Main Universal Connector Block implementation
 */
export class UniversalConnectorBlock {
  private appName: string;
  private version: string;
  private basePath: string;
  private endpoints: Endpoint[];
  private circuitBreaker: CircuitBreaker;
  private rateLimiter: RateLimiter;
  private cacher: Cacher;
  
  constructor(appName: string, version: string, basePath = '/api') {
    this.appName = appName;
    this.version = version;
    this.basePath = basePath;
    this.endpoints = [];
    this.circuitBreaker = new CircuitBreaker();
    this.rateLimiter = new RateLimiter();
    this.cacher = new Cacher();
  }
  
  /**
   * Generate a USS-compliant API descriptor
   */
  generateDescriptor(): UssDescriptor {
    return {
      '@context': 'https://uip.org/context/v1',
      '@type': 'APIDescriptor',
      '@id': `https://api.example.com/${this.appName}`,
      'version': this.version,
      'name': this.appName,
      'basePath': this.basePath,
      'endpoints': this.endpoints.map(endpoint => this.endpointToUss(endpoint))
    };
  }
  
  /**
   * Convert an Endpoint to USS format
   */
  private endpointToUss(endpoint: Endpoint): Record<string, any> {
    return {
      'path': endpoint.path,
      'method': endpoint.method,
      'parameters': endpoint.parameters.map(param => ({
        'name': param.name,
        'location': param.location,
        'required': param.required,
        'type': param.type,
        'description': param.description
      })),
      'responses': endpoint.responses.map(resp => ({
        'statusCode': resp.statusCode,
        'contentType': resp.contentType,
        'schema': resp.schema,
        'description': resp.description
      })),
      'authentication': {
        'required': endpoint.authRequired,
        'methods': endpoint.authMethods
      },
      'rateLimit': endpoint.rateLimit,
      'description': endpoint.description
    };
  }
  
  /**
   * Register an API endpoint with the UCB
   */
  registerEndpoint(
    path: string,
    method: HttpMethod,
    parameters: Parameter[] = [],
    responses: Response[] = [],
    authRequired: boolean = true,
    authMethods: AuthMethod[] = [AuthMethod.BEARER],
    rateLimit?: number,
    description?: string
  ): void {
    const endpoint: Endpoint = {
      path,
      method,
      parameters,
      responses: [...responses],
      authRequired,
      authMethods,
      rateLimit,
      description
    };
    
    // Add default error responses if not provided
    if (!endpoint.responses.some(r => r.statusCode === 400)) {
      endpoint.responses.push({
        statusCode: 400,
        contentType: 'application/json',
        schema: { type: 'Error' },
        description: 'Bad Request'
      });
    }
    
    if (!endpoint.responses.some(r => r.statusCode === 500)) {
      endpoint.responses.push({
        statusCode: 500,
        contentType: 'application/json',
        schema: { type: 'Error' },
        description: 'Internal Server Error'
      });
    }
    
    this.endpoints.push(endpoint);
  }
  
  /**
   * Convert native TypeScript data to USS format
   */
  standardizeOutput(nativeData: any): string {
    // Determine the USS type
    const ussType = TypeMapper.inferTypeFromValue(nativeData);
    
    // Create the standardized output
    const result = {
      data: nativeData,
      metadata: {
        type: ussType,
        timestamp: new Date().toISOString()
      }
    };
    
    // Convert to JSON
    return JSON.stringify(result);
  }
  
  /**
   * Convert USS format back to native TypeScript data
   */
  translateInput(universalData: string, expectedType?: UssType): any {
    try {
      const parsed = JSON.parse(universalData);
      
      // Validate structure
      if (typeof parsed !== 'object' || parsed === null || !('data' in parsed)) {
        throw new ValidationError('Invalid USS format: missing "data" field', [
          { received: parsed === null ? 'null' : typeof parsed === 'object' ? Object.keys(parsed) : typeof parsed }
        ]);
      }
      
      const data = parsed.data;
      
      // If expected_type is provided, validate and convert
      if (expectedType) {
        return TypeMapper.validateAndConvert(data, expectedType);
      }
      
      return data;
    } catch (e) {
      if (e instanceof SyntaxError) {
        throw new ValidationError('Invalid JSON data', [{ error: e.message }]);
      }
      throw e;
    }
  }
  
  /**
   * Call a remote API with resilience patterns and error handling
   */
  async callRemoteApi<T>(
    url: string,
    options: RequestOptions = {},
    auth?: AuthOptions
  ): Promise<T> {
    // Default options
    const defaultOptions: RequestOptions = {
      method: 'GET',
      headers: {},
      useCache: false,
      retryAttempts: 3,
      timeout: 30000
    };
    
    // Merge with provided options
    const mergedOptions: RequestOptions = {
      ...defaultOptions,
      ...options,
      headers: { ...defaultOptions.headers, ...options.headers }
    };
    
    // Check circuit breaker
    if (!this.circuitBreaker.allowRequest()) {
      throw new UcbError(
        'CIRCUIT_OPEN',
        'Circuit breaker is open due to repeated failures',
        [],
        503
      );
    }
    
    // Check rate limiter
    if (!this.rateLimiter.allowRequest()) {
      throw new UcbError(
        'RATE_LIMIT_EXCEEDED',
        'Rate limit exceeded for API calls',
        [],
        429
      );
    }
    
    // Check cache if enabled
    if (mergedOptions.useCache && mergedOptions.method?.toUpperCase() === 'GET') {
      const cacheKey = this.cacher.generateKey(url, mergedOptions);
      const cachedResponse = this.cacher.get<T>(cacheKey);
      if (cachedResponse) {
        console.debug(`Cache hit for ${url}`);
        return cachedResponse;
      }
    }
    
    // Prepare headers
    const headers = new Headers(mergedOptions.headers);
    
    // Add default headers if not present
    if (!headers.has('Accept')) {
      headers.set('Accept', 'application/json');
    }
    
    if (!headers.has('Content-Type') && mergedOptions.body) {
      headers.set('Content-Type', 'application/json');
    }
    
    // Prepare authentication
    if (auth) {
      const authType = auth.type || 'bearer';
      
      switch (authType) {
        case 'bearer':
          headers.set('Authorization', `Bearer ${auth.token || ''}`);
          break;
        case 'basic':
          const username = auth.username || '';
          const password = auth.password || '';
          const base64Auth = btoa(`${username}:${password}`);
          headers.set('Authorization', `Basic ${base64Auth}`);
          break;
        case 'api_key':
          const keyName = auth.keyName || 'api_key';
          const keyValue = auth.keyValue || '';
          const keyLocation = auth.keyLocation || 'header';
          
          if (keyLocation === 'header') {
            headers.set(keyName, keyValue);
          } else if (keyLocation === 'query') {
            const separator = url.includes('?') ? '&' : '?';
            url = `${url}${separator}${keyName}=${encodeURIComponent(keyValue)}`;
          }
          break;
      }
    }
    
    // Prepare the request
    const requestInit: RequestInit = {
      method: mergedOptions.method,
      headers
    };
    
    // Add body if provided
    if (mergedOptions.body) {
      if (headers.get('Content-Type') === 'application/json') {
        requestInit.body = JSON.stringify(mergedOptions.body);
      } else {
        requestInit.body = mergedOptions.body as BodyInit;
      }
    }
    
    // Set up AbortController for timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), mergedOptions.timeout);
    requestInit.signal = controller.signal;
    
    // Execute request with retry logic
    let attempt = 0;
    let lastError: UcbError | null = null;
    
    while (attempt < (mergedOptions.retryAttempts || 1)) {
      try {
        attempt++;
        
        // Make the request
        const response = await fetch(url, requestInit);
        
        // Clear the timeout
        clearTimeout(timeoutId);
        
        // Check for HTTP errors
        if (!response.ok) {
          let errorMsg = `API request failed with status ${response.status}`;
          let errorDetails: ErrorDetail[] = [];
          
          try {
            const errorData = await response.json();
            if (typeof errorData === 'object' && errorData !== null) {
              errorMsg = errorData.message || errorMsg;
              errorDetails = errorData.details || [];
            }
          } catch {}
          
          if (response.status >= 500) {
            // Server error, may retry
            lastError = new UcbError(
              `REMOTE_SERVER_ERROR_${response.status}`,
              errorMsg,
              errorDetails,
              response.status
            );
            console.warn(`Server error on attempt ${attempt}: ${errorMsg}`);
            
            if (attempt < (mergedOptions.retryAttempts || 1)) {
              // Exponential backoff
              const backoffTime = 500 * Math.pow(2, attempt - 1);
              console.info(`Retrying in ${backoffTime}ms...`);
              await new Promise(resolve => setTimeout(resolve, backoffTime));
              continue;
            }
          } else {
            // Client error, don't retry
            this.circuitBreaker.recordSuccess(); // Don't penalize for 4xx errors
            throw new UcbError(
              `REMOTE_CLIENT_ERROR_${response.status}`,
              errorMsg,
              errorDetails,
              response.status
            );
          }
        }
        
        // Process successful response
        let result: T;
        const contentType = response.headers.get('Content-Type');
        
        if (contentType?.includes('application/json')) {
          result = await response.json();
        } else {
          const text = await response.text();
          result = { raw_content: text } as unknown as T;
        }
        
        // Record success
        this.circuitBreaker.recordSuccess();
        
        // Cache the result if enabled
        if (mergedOptions.useCache && mergedOptions.method?.toUpperCase() === 'GET') {
          const cacheKey = this.cacher.generateKey(url, mergedOptions);
          this.cacher.set(cacheKey, result);
        }
        
        return result;
      } catch (e) {
        console.warn(`Request failed on attempt ${attempt}: ${e instanceof Error ? e.message : String(e)}`);
        
        // Handle AbortError (timeout)
        if (e instanceof DOMException && e.name === 'AbortError') {
          lastError = new UcbError(
            'TIMEOUT_ERROR',
            `Request timed out after ${mergedOptions.timeout}ms`,
            [],
            408
          );
        } else if (e instanceof UcbError) {
          lastError = e;
        } else {
          lastError = new UcbError(
            'CONNECTION_ERROR',
            `Connection error: ${e instanceof Error ? e.message : String(e)}`,
            [],
            503
          );
        }
        
        if (attempt < (mergedOptions.retryAttempts || 1)) {
          // Exponential backoff
          const backoffTime = 500 * Math.pow(2, attempt - 1);
          console.info(`Retrying in ${backoffTime}ms...`);
          await new Promise(resolve => setTimeout(resolve, backoffTime));
        } else {
          // Record failure after all retries
          this.circuitBreaker.recordFailure();
          clearTimeout(timeoutId);
        }
      }
    }
    
    // If we got here, all retries failed
    if (lastError) {
      throw lastError;
    } else {
      throw new UcbError(
        'MAX_RETRIES_EXCEEDED',
        `Request failed after ${mergedOptions.retryAttempts} attempts`,
        [],
        503
      );
    }
  }
  
  /**
   * Returns the USS API descriptor as a JSON string
   */
  exposeDescriptor(): string {
    const descriptor = this.generateDescriptor();
    return JSON.stringify(descriptor);
  }
}

// Example usage
if (typeof window !== 'undefined') {
  // Browser environment
  (window as any).UniversalConnectorBlock = UniversalConnectorBlock;
}

export default UniversalConnectorBlock;