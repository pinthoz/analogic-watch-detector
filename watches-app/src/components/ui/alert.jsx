import PropTypes from 'prop-types';

export function Alert({ variant = 'default', className = '', children, ...props }) {
    const variants = {
      default: 'bg-background text-foreground',
      destructive: 'bg-destructive/15 text-destructive dark:bg-destructive dark:text-destructive-foreground',
    };
  
    return (
      <div
        role="alert"
        className={`relative w-full rounded-lg border p-4 [&>svg~*]:pl-7 [&>svg+div]:translate-y-[-3px] [&>svg]:absolute [&>svg]:left-4 [&>svg]:top-4 [&>svg]:text-foreground ${variants[variant]} ${className}`}
        {...props}
      >
        {children}
      </div>
    );
  }
  
  Alert.propTypes = {
    variant: PropTypes.oneOf(['default', 'destructive']),
    className: PropTypes.string,
    children: PropTypes.node,
  };
  
  Alert.defaultProps = {
    variant: 'default',
    className: '',
  };
  
  export function AlertDescription({ className = '', children, ...props }) {
    return (
      <div className={`text-sm [&_p]:leading-relaxed ${className}`} {...props}>
        {children}
      </div>
    );
  }
  
  AlertDescription.propTypes = {
    className: PropTypes.string,
    children: PropTypes.node,
  };
  
  AlertDescription.defaultProps = {
    className: '',
  };