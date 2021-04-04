# Author: Mark T w17006267
# this class represents a user

class User:

    #member variables - these should not be accessed directly
    m_pushUps = 0;
    m_sitUps = 0;
    m_pullUps = 0;

    #get methods
    def GetPushUps(self):
        return self.m_sitUps;

    def GetSitUps(self):
        return self.m_sitUps;

    def GetPullUps(self):
        return self.m_pullUps;

    def GetTotal(self):
        return (self.m_pullUps + self.m_sitUps + self.m_sitUps);


    #set methods
    def SetPushUps(self, _x):
        self.m_pushUps = _x;

    def SetSitUps(self, _x):
        self.m_sitUps = _x;

    def SetPullUps(self, _x):
        self.m_pullUps = _x;
