import { useCallback, useEffect } from 'react';
import { useHistory } from 'react-router';
import { Button } from '@/components';
import { Space } from '@/components/Space/Space';
import { useContextProps } from '@/providers/RoutesProvider';

export const ProjectCollection = () => {
  const setContextProps = useContextProps();
  const history = useHistory();

  const back = useCallback(() => {
    history.push('/projects');
  }, []);
  const openModal = () => {};

  useEffect(() => {
    setContextProps({ back, openModal });
  }, []);

  return <>ProjectCollection</>;
};
ProjectCollection.path = '/collections';
ProjectCollection.title = t("Project collection");
ProjectCollection.exact = true;
ProjectCollection.context = ({ back, openModal }) => {
  return <Space>
    <Button onClick={back} size="compact">{t("Back", "返回")}</Button>
    <Button onClick={openModal} look="primary" size="compact">{t("Create Project Collection", "新增集合")}</Button>
  </Space>;
};
