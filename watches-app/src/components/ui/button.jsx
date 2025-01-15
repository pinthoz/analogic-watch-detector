import PropTypes from 'prop-types';


export function Button({ className = '', variant = 'default', disabled, children, ...props }) {
    const baseStyles = 'inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none ring-offset-background';
    
    const variants = {
      default: 'bg-primary text-primary-foreground hover:bg-primary/90',
      outline: 'border border-input hover:bg-accent hover:text-accent-foreground',
      destructive: 'bg-destructive text-destructive-foreground hover:bg-destructive/90',
    };
  
    return (
      <button
        className={`${baseStyles} ${variants[variant]} ${className}`}
        disabled={disabled}
        {...props}
      >
        {children}
      </button>
    );
  }
  
  Button.propTypes = {
    className: PropTypes.string,
    variant: PropTypes.oneOf(['default', 'outline', 'destructive']),
    disabled: PropTypes.bool,
    children: PropTypes.node,
    onClick: PropTypes.func,
  };
  
  Button.defaultProps = {
    className: '',
    variant: 'default',
    disabled: false,
  };