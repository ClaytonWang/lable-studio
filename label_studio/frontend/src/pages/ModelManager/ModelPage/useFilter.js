import { useCallback, useContext, useEffect,useState } from "react";
import { ApiContext } from '../../../providers/ApiProvider';

export const useFilter = () => {
  const api = useContext(ApiContext);
  const [fields, setFields] = useState({});

  const getFields = useCallback(async () => {
    const reps = await api.callApi('filtersModel');

    return reps;
  }, []);

  useEffect(async () => {
    const data = await getFields();

    setFields(data);

  },[]);

  return fields;
};
