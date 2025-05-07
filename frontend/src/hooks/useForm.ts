import { useState, useCallback, ChangeEvent } from 'react';
import { ValidationResult, validateForm } from '../utils/validation';

/**
 * Form state interface
 */
interface FormState<T> {
  values: T;
  errors: Record<string, string | undefined>;
  touched: Record<string, boolean>;
  isValid: boolean;
  isSubmitting: boolean;
}

/**
 * Form options interface
 */
interface FormOptions<T> {
  initialValues: T;
  validationSchema?: Record<string, (value: any) => ValidationResult>;
  onSubmit: (values: T) => Promise<void> | void;
}

/**
 * Get a nested value from an object using a path string
 * @param obj The object to get the value from
 * @param path The path to the value (e.g. 'user.name')
 */
function getNestedValue(obj: any, path: string): any {
  return path.split('.').reduce((prev, curr) => {
    return prev && prev[curr] !== undefined ? prev[curr] : undefined;
  }, obj);
}

/**
 * Set a nested value in an object using a path string
 * @param obj The object to set the value in
 * @param path The path to set the value at (e.g. 'user.name')
 * @param value The value to set
 */
function setNestedValue(obj: any, path: string, value: any): any {
  const result = { ...obj };
  const parts = path.split('.');
  let current = result;
  
  for (let i = 0; i < parts.length - 1; i++) {
    const part = parts[i];
    current[part] = current[part] !== undefined ? { ...current[part] } : {};
    current = current[part];
  }
  
  current[parts[parts.length - 1]] = value;
  return result;
}

/**
 * Custom hook for managing form state and validation
 */
function useForm<T extends Record<string, any>>(options: FormOptions<T>) {
  const { initialValues, validationSchema = {}, onSubmit } = options;

  const [formState, setFormState] = useState<FormState<T>>({
    values: initialValues,
    errors: {},
    touched: {},
    isValid: Object.keys(validationSchema).length === 0,
    isSubmitting: false,
  });

  // Validate form values
  const validateValues = useCallback(
    (values: T) => {
      if (Object.keys(validationSchema).length === 0) {
        return { isValid: true, errors: {} };
      }

      return validateForm(values, validationSchema);
    },
    [validationSchema]
  );

  // Handle field change
  const handleChange = useCallback(
    (e: ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
      const { name, value, type } = e.target;
      
      // Handle checkbox inputs
      const fieldValue = type === 'checkbox' 
        ? (e.target as HTMLInputElement).checked 
        : value;
      
      // Update form state
      setFormState((prev) => {
        const newValues = setNestedValue(prev.values, name, fieldValue);
        const { isValid, errors } = validateValues(newValues);

        return {
          ...prev,
          values: newValues,
          errors,
          isValid,
        };
      });
    },
    [validateValues]
  );

  // Handle field blur
  const handleBlur = useCallback((e: ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name } = e.target;
    
    setFormState((prev) => ({
      ...prev,
      touched: { ...prev.touched, [name]: true },
    }));
  }, []);

  // Set custom value
  const setValue = useCallback(
    (name: string, value: any) => {
      setFormState((prev) => {
        const newValues = setNestedValue(prev.values, name, value);
        const { isValid, errors } = validateValues(newValues);

        return {
          ...prev,
          values: newValues,
          errors,
          isValid,
        };
      });
    },
    [validateValues]
  );

  // Reset form to initial values
  const resetForm = useCallback(() => {
    setFormState({
      values: initialValues,
      errors: {},
      touched: {},
      isValid: Object.keys(validationSchema).length === 0,
      isSubmitting: false,
    });
  }, [initialValues, validationSchema]);

  // Handle form submission
  const handleSubmit = useCallback(
    async (e: React.FormEvent<HTMLFormElement>) => {
      e.preventDefault();
      
      // Validate form
      const { isValid, errors } = validateValues(formState.values);
      
      // Mark all fields with errors as touched
      const touchedAll = { ...formState.touched };
      Object.keys(errors).forEach(key => {
        if (errors[key]) {
          touchedAll[key] = true;
        }
      });
      
      // Update form state
      setFormState((prev) => ({
        ...prev,
        touched: touchedAll,
        errors,
        isValid,
        isSubmitting: isValid,
      }));
      
      // If form is valid, call onSubmit
      if (isValid) {
        try {
          await onSubmit(formState.values);
        } catch (error) {
          console.error('Form submission error:', error);
        } finally {
          setFormState((prev) => ({
            ...prev,
            isSubmitting: false,
          }));
        }
      }
    },
    [formState.values, formState.touched, onSubmit, validateValues]
  );

  return {
    ...formState,
    handleChange,
    handleBlur,
    handleSubmit,
    setValue,
    resetForm,
    getNestedValue,
  };
}

export default useForm;
