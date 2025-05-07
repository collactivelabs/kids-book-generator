/**
 * Validation utility functions for form validation
 */

/**
 * Validation result interface
 */
export interface ValidationResult {
  isValid: boolean;
  error?: string;
}

/**
 * Required field validation
 * @param value Value to validate
 * @param fieldName Optional field name for error message
 * @returns Validation result
 */
export const required = (value: any, fieldName = 'This field'): ValidationResult => {
  if (value === undefined || value === null || value === '') {
    return {
      isValid: false,
      error: `${fieldName} is required`,
    };
  }
  
  return { isValid: true };
};

/**
 * Email validation
 * @param value Email to validate
 * @returns Validation result
 */
export const isEmail = (value: string): ValidationResult => {
  if (!value) {
    return { isValid: true }; // If empty, let required validation handle it
  }
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  
  if (!emailRegex.test(value)) {
    return {
      isValid: false,
      error: 'Please enter a valid email address',
    };
  }
  
  return { isValid: true };
};

/**
 * Minimum length validation
 * @param value Value to validate
 * @param minLength Minimum length
 * @param fieldName Optional field name for error message
 * @returns Validation result
 */
export const minLength = (value: string, minLength: number, fieldName = 'This field'): ValidationResult => {
  if (!value) {
    return { isValid: true }; // If empty, let required validation handle it
  }
  
  if (value.length < minLength) {
    return {
      isValid: false,
      error: `${fieldName} must be at least ${minLength} characters`,
    };
  }
  
  return { isValid: true };
};

/**
 * Maximum length validation
 * @param value Value to validate
 * @param maxLength Maximum length
 * @param fieldName Optional field name for error message
 * @returns Validation result
 */
export const maxLength = (value: string, maxLength: number, fieldName = 'This field'): ValidationResult => {
  if (!value) {
    return { isValid: true }; // If empty, let required validation handle it
  }
  
  if (value.length > maxLength) {
    return {
      isValid: false,
      error: `${fieldName} must be at most ${maxLength} characters`,
    };
  }
  
  return { isValid: true };
};

/**
 * Match validation (e.g., for password confirmation)
 * @param value Value to validate
 * @param matchValue Value to match against
 * @param fieldName Optional field name for error message
 * @returns Validation result
 */
export const matches = (value: string, matchValue: string, fieldName = 'This field'): ValidationResult => {
  if (!value || !matchValue) {
    return { isValid: true }; // If empty, let required validation handle it
  }
  
  if (value !== matchValue) {
    return {
      isValid: false,
      error: `${fieldName} does not match`,
    };
  }
  
  return { isValid: true };
};

/**
 * Number range validation
 * @param value Value to validate
 * @param min Minimum value
 * @param max Maximum value
 * @param fieldName Optional field name for error message
 * @returns Validation result
 */
export const numberRange = (
  value: number, 
  min: number, 
  max: number, 
  fieldName = 'This field'
): ValidationResult => {
  if (value === undefined || value === null) {
    return { isValid: true }; // If empty, let required validation handle it
  }
  
  if (value < min || value > max) {
    return {
      isValid: false,
      error: `${fieldName} must be between ${min} and ${max}`,
    };
  }
  
  return { isValid: true };
};

/**
 * Compose multiple validations
 * @param validators Validation functions to compose
 * @returns Composed validation function
 */
export const composeValidators = (...validators: ((value: any) => ValidationResult)[]) => 
  (value: any): ValidationResult => {
    for (const validator of validators) {
      const result = validator(value);
      if (!result.isValid) {
        return result;
      }
    }
    
    return { isValid: true };
  };

/**
 * Form validation helper for handling multiple fields
 * @param values Form values
 * @param validationSchema Validation schema with field names and validation functions
 * @returns Validation result with errors for each field
 */
export const validateForm = (
  values: Record<string, any>, 
  validationSchema: Record<string, (value: any) => ValidationResult>
): { isValid: boolean; errors: Record<string, string | undefined> } => {
  const errors: Record<string, string | undefined> = {};
  let isValid = true;
  
  for (const field in validationSchema) {
    if (Object.prototype.hasOwnProperty.call(validationSchema, field)) {
      const validate = validationSchema[field];
      const result = validate(values[field]);
      
      if (!result.isValid) {
        errors[field] = result.error;
        isValid = false;
      } else {
        errors[field] = undefined;
      }
    }
  }
  
  return { isValid, errors };
};
