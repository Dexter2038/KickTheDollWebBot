import { useEffect, useState } from "react";

interface NumberInputProps {
    value?: string;
    onChange: (newValue: string) => void;
    placeholder?: string;
    className?: string;
    maxLength?: number;
    disabled?: boolean;
    style?: React.CSSProperties;
}

function NumberInput({
    value,
    onChange,
    placeholder,
    className,
    maxLength,
    disabled,
    style,
}: NumberInputProps) {
    const [inputValue, setInputValue] = useState(value || "");

    // Add commas (thousands separators) as the user types
    useEffect(() => {
        const formattedValue = inputValue
            .replace(/[^0-9]/g, "") // Remove non-digit characters
            .replace(/\B(?=(\d{3})+(?!\d))/g, ","); // Add commas
        setInputValue(formattedValue);
    }, [inputValue]);

    // Handle input changes
    const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const newValue = event.target.value.replace(/[^0-9]/g, ""); // Allow only digits
        setInputValue(newValue);
        onChange(newValue); // Pass the raw value to the parent component
    };
    return (
        <input
            style={{ ...style, textAlign: "center" }}
            type="text"
            value={inputValue}
            onChange={handleChange}
            placeholder={placeholder}
            className={className}
            maxLength={maxLength}
            disabled={disabled}
        />
    );
}

export default NumberInput;
