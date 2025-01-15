import PropTypes from 'prop-types';


export function Progress({ value = 0, className = '', ...props }) {
    return (
      <div className={`relative h-4 w-full overflow-hidden rounded-full bg-secondary ${className}`} {...props}>
        <div
          className="h-full w-full flex-1 bg-primary transition-all"
          style={{ transform: `translateX(-${100 - (value || 0)}%)` }}
        />
      </div>
    );
  }
  
  Progress.propTypes = {
    value: PropTypes.number,
    className: PropTypes.string,
  };
  
  Progress.defaultProps = {
    value: 0,
    className: '',
  };