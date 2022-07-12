import { useMemo } from "react";
import { Typography } from "antd";
import { diffChars } from "diff";

const { Text } = Typography;

export const DiffChars = ({ oldValue, newValue }) => {
  const element = useMemo(() => {
    const different = diffChars(oldValue, newValue);

    return different.map((item, index) => {
      const v = (() => {
        if (item.removed) {
          return (
            <Text type="danger" delete>
              {item.value}
            </Text>
          );
        }
        if (item.added) {
          return <Text type="success">{item.value}</Text>;
        }
        return <Text>{item.value}</Text>;
      })();

      return <span key={index}>{v}</span>;
    });
  }, [oldValue, newValue]);

  return <>{element}</>;
};
