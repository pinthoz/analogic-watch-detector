import PropTypes from 'prop-types';

// components/ui/card.jsx
export function Card({ className = '', children, ...props }) {
    return (
      <div className={`rounded-lg border bg-card text-card-foreground shadow-sm ${className}`} {...props}>
        {children}
      </div>
    );
  }
  
  Card.propTypes = {
    className: PropTypes.string,
    children: PropTypes.node,
  };
  
  Card.defaultProps = {
    className: '',
  };
  
  export function CardHeader({ className = '', children, ...props }) {
    return (
      <div className={`flex flex-col space-y-1.5 p-6 ${className}`} {...props}>
        {children}
      </div>
    );
  }
  
  CardHeader.propTypes = {
    className: PropTypes.string,
    children: PropTypes.node,
  };
  
  CardHeader.defaultProps = {
    className: '',
  };
  
  export function CardTitle({ className = '', children, ...props }) {
    return (
      <h3 className={`text-2xl font-semibold leading-none tracking-tight ${className}`} {...props}>
        {children}
      </h3>
    );
  }
  
  CardTitle.propTypes = {
    className: PropTypes.string,
    children: PropTypes.node,
  };
  
  CardTitle.defaultProps = {
    className: '',
  };
  
  export function CardContent({ className = '', children, ...props }) {
    return (
      <div className={`p-6 pt-0 ${className}`} {...props}>
        {children}
      </div>
    );
  }
  
  CardContent.propTypes = {
    className: PropTypes.string,
    children: PropTypes.node,
  };
  
  CardContent.defaultProps = {
    className: '',
  };